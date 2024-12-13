import argparse
import re
import yaml

def parse_config(config_text):
    constants = {}

    def evaluate_constants(match):
        name = match.group(1)
        if name not in constants:
            raise ValueError(f"Undefined constant: {name}")
        return str(constants[name])

    # Убираем комментарии
    config_text = re.sub(r"#.*", "", config_text)
    config_text = re.sub(r"/\*.*?\*/", "", config_text, flags=re.DOTALL)

    # Парсим переменные
    for match in re.finditer(r"var\s+([_a-z]+)\s+(\S+)", config_text):
        name, value = match.groups()
        constants[name] = value

    # Заменяем переменные на их значения
    config_text = re.sub(r"\$\[([_a-z]+)\]", evaluate_constants, config_text)

    def parse_value(value):
        value = value.strip()
        
        # Проверка для значений, обернутых в q()
        if value.startswith('q(') and value.endswith(')'):
            # Извлекаем значение внутри q() и проверяем на соответствие
            inner_value = value[2:-1]  # Убираем q()
            if re.match(r'^[a-z_]+$', inner_value):  # Проверяем, что внутри только _ и a-z
                return inner_value
            else:
                # Если значение не проходит проверку, возвращаем None (игнорируем это значение)
                return None
        
        # Проверка, если значение является числом (целым или булевым)
        if value.isdigit():
            return int(value)
        elif value == '1':
            return True
        elif value == '0':
            return False
        
        # Если значение не строка через q() и не число, выбрасываем ошибку
        raise ValueError(f"Invalid value: {value}")
    
    def parse_dict(text):
        result = {}
        used_variables = set()  # Множество для отслеживания использованных переменных

        # Пропускаем строки, начинающиеся с var, и не добавляем их в итоговый результат
        text = re.sub(r"var\s+\w+\s+q\((.*?)\)|var\s+\w+\s+(\d+)", "", text)

        # Парсим блоки
        block_pattern = r'(\w+)\s*=\s*\{(.*?)\}'
        blocks = re.findall(block_pattern, text, re.DOTALL)

        for key, block in blocks:
            sub_result = {}
            
            block_lines = [line.strip() for line in block.split(',') if line.strip()]
            for line in block_lines:
                if '=' in line:
                    key_value = line.split('=')
                    if len(key_value) == 2:
                        sub_key, sub_value = key_value
                        sub_key = sub_key.strip()
                        sub_value = sub_value.strip()

                        # Если значение не прошло проверку, пропускаем его
                        parsed_value = parse_value(sub_value)
                        if parsed_value is not None:
                            sub_result[sub_key] = parsed_value
                            used_variables.add(sub_key)  # Отметим, что эта переменная использована
                        
            result[key] = sub_result

        # Добавляем переменные, которые не находятся в блоках, но используются
        non_block_vars = re.findall(r'(\w+)\s*=\s*([^,{}]+)', text)

        # Фильтрация: удаляем переменные с пустыми значениями и пробелами
        non_block_vars = [(key.strip(), value.strip()) for key, value in non_block_vars if key.strip() and value.strip()]
        
        for key, value in non_block_vars:
            if key not in used_variables and value != "":  # Проверяем, что значение не пустое
                parsed_value = parse_value(value.strip())
                if parsed_value is not None:  # Если значение не None (то есть валидное)
                    result[key] = parsed_value

        return result

    parsed_data = parse_dict(config_text)

    return parsed_data

def main():
    parser = argparse.ArgumentParser(description="Config Language to YAML Converter")
    parser.add_argument("--input", required=True, help="Path to input file with config text")
    parser.add_argument("--output", required=True, help="Path to output YAML file")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as infile:
            config_text = infile.read()

        parsed_data = parse_config(config_text)

        with open(args.output, "w", encoding="utf-8") as outfile:
            yaml.dump(parsed_data, outfile, allow_unicode=True, default_flow_style=False)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
