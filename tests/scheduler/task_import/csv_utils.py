#  Drakkar-Software OctoBot-Node
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

import csv
import json
import os
from typing import Dict, List, Optional

import octobot_commons.cryptography as cryptography
from octobot_node.scheduler.encryption.task_inputs import (
    encrypt_task_content,
    decrypt_task_content,
)

################################################################################
# This file is used to test the functions inside octobot_node/ui/src/lib/csv.ts
# It provides Python implementations of the CSV column merging logic to verify
# that the TypeScript implementation behaves correctly.
################################################################################

COLUMN_NAME = "name"
COLUMN_CONTENT = "content"
COLUMN_TYPE = "type"
CONTENT_SEPARATOR = ";"

REQUIRED_KEYS = [COLUMN_NAME, COLUMN_TYPE]
KEYS_OUTSIDE_CONTENT = [COLUMN_NAME, COLUMN_TYPE]

DEFAULT_KEYS_FILE = "task_encryption_keys.json"

KEY_NAMES = {
    "TASKS_INPUTS_RSA_PUBLIC_KEY": "tasks_inputs_rsa_public_key",
    "TASKS_INPUTS_RSA_PRIVATE_KEY": "tasks_inputs_rsa_private_key",
    "TASKS_INPUTS_ECDSA_PUBLIC_KEY": "tasks_inputs_ecdsa_public_key",
    "TASKS_INPUTS_ECDSA_PRIVATE_KEY": "tasks_inputs_ecdsa_private_key",
    "TASKS_OUTPUTS_RSA_PUBLIC_KEY": "tasks_outputs_rsa_public_key",
    "TASKS_OUTPUTS_RSA_PRIVATE_KEY": "tasks_outputs_rsa_private_key",
    "TASKS_OUTPUTS_ECDSA_PUBLIC_KEY": "tasks_outputs_ecdsa_public_key",
    "TASKS_OUTPUTS_ECDSA_PRIVATE_KEY": "tasks_outputs_ecdsa_private_key",
}


def find_column_index(column_names: List[str], key: str) -> int:
    for i, col in enumerate(column_names):
        if col.lower() == key.lower():
            return i
    return -1


def validate_required_keys(column_names: List[str]) -> Dict[int, str]:
    required_keys_indices: Dict[int, str] = {}
    for key in REQUIRED_KEYS:
        index = find_column_index(column_names, key)
        if index == -1:
            raise ValueError(f"Required key '{key}' not found in CSV header")
        required_keys_indices[index] = key
    return required_keys_indices


def find_keys_outside_content_indices(column_names: List[str]) -> Dict[int, str]:
    indices: Dict[int, str] = {}
    for key in KEYS_OUTSIDE_CONTENT:
        index = find_column_index(column_names, key)
        if index != -1:
            indices[index] = key
    return indices


def build_content(
    values: List[str],
    column_names: List[str],
    keys_outside_content_indices: Dict[int, str],
    content_column_index: int
) -> str:
    content_parts: List[str] = []
    
    for i in range(min(len(column_names), len(values))):
        if i not in keys_outside_content_indices and i != content_column_index:
            value = values[i].strip() if i < len(values) else ""
            if value:
                column_name = column_names[i]
                upper_key = column_name.upper()
                content_parts.append(f"{upper_key}={value}")
    
    concatenated_content = CONTENT_SEPARATOR.join(content_parts)
    if content_column_index != -1 and content_column_index < len(values):
        content_column_value = values[content_column_index].strip()
        if content_column_value:
            if concatenated_content:
                return f"{concatenated_content}{CONTENT_SEPARATOR}{content_column_value}"
            return content_column_value
    
    return concatenated_content


def validate_row_has_required_keys(
    values: List[str],
    required_keys_indices: Dict[int, str]
) -> bool:
    for index in required_keys_indices:
        if index >= len(values) or not values[index].strip():
            return False
    return True


def process_row(
    values: List[str],
    column_names: List[str],
    required_keys_indices: Dict[int, str],
    keys_outside_content_indices: Dict[int, str],
    content_column_index: int
) -> Optional[Dict[str, str]]:
    if not values or all(not v.strip() for v in values):
        return None
    
    while len(values) < len(column_names):
        values.append("")
    
    if not validate_row_has_required_keys(values, required_keys_indices):
        return None
    
    keys_outside_content_values: Dict[str, str] = {}
    for index, key in keys_outside_content_indices.items():
        if index < len(values):
            value = values[index].strip()
            if value:
                keys_outside_content_values[key] = value
    
    final_content = build_content(
        values,
        column_names,
        keys_outside_content_indices,
        content_column_index
    )
    
    return {
        COLUMN_NAME: keys_outside_content_values.get(COLUMN_NAME, ""),
        COLUMN_CONTENT: final_content,
        COLUMN_TYPE: keys_outside_content_values.get(COLUMN_TYPE, ""),
    }


def parse_csv(input_file_path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    
    with open(input_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        try:
            column_names = next(reader)
        except StopIteration:
            raise ValueError("No header found in CSV file")
        
        column_names = [col.strip() for col in column_names if col.strip()]
        
        if not column_names:
            raise ValueError("No column names found in CSV header")
        
        required_keys_indices = validate_required_keys(column_names)
        keys_outside_content_indices = find_keys_outside_content_indices(column_names)
        content_column_index = find_column_index(column_names, COLUMN_CONTENT)
        
        for row_values in reader:
            try:
                processed_row = process_row(
                    row_values,
                    column_names,
                    required_keys_indices,
                    keys_outside_content_indices,
                    content_column_index
                )
                if processed_row is not None:
                    rows.append(processed_row)
            except Exception as e:
                print(f"Failed to process CSV row: {e}")
                continue
    
    return rows


def escape_csv_value(value: str) -> str:
    if not value:
        return ""
    
    if ',' in value or '"' in value or '\n' in value:
        escaped_value = value.replace('"', '""')
        return f'"{escaped_value}"'
    
    return value


def generate_csv(rows: List[Dict[str, str]], output_file_path: str) -> None:
    headers = [COLUMN_NAME, COLUMN_CONTENT, COLUMN_TYPE]
    
    with open(output_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([
                row.get(COLUMN_NAME, ""),
                row.get(COLUMN_CONTENT, ""),
                row.get(COLUMN_TYPE, "")
            ])


def merge_csv_columns(input_file_path: str, output_file_path: str) -> None:
    rows = parse_csv(input_file_path)
    generate_csv(rows, output_file_path)


def generate_and_save_keys(keys_file_path: str = DEFAULT_KEYS_FILE) -> Dict[str, str]:
    if os.path.exists(keys_file_path):
        print(f"Keys file already exists at {keys_file_path}. Loading existing keys...")
        with open(keys_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    print(f"Generating new encryption keys and saving to {keys_file_path}...")
    
    keys: Dict[str, str] = {}
    
    print("Generating RSA key pair for task inputs...")
    rsa_private_key, rsa_public_key = cryptography.generate_rsa_key_pair(key_size=4096)
    keys[KEY_NAMES["TASKS_INPUTS_RSA_PRIVATE_KEY"]] = rsa_private_key.decode('utf-8')
    keys[KEY_NAMES["TASKS_INPUTS_RSA_PUBLIC_KEY"]] = rsa_public_key.decode('utf-8')
    
    print("Generating ECDSA key pair for task inputs...")
    ecdsa_private_key, ecdsa_public_key = cryptography.generate_ecdsa_key_pair()
    keys[KEY_NAMES["TASKS_INPUTS_ECDSA_PRIVATE_KEY"]] = ecdsa_private_key.decode('utf-8')
    keys[KEY_NAMES["TASKS_INPUTS_ECDSA_PUBLIC_KEY"]] = ecdsa_public_key.decode('utf-8')
    
    print("Generating RSA key pair for task outputs...")
    rsa_private_key, rsa_public_key = cryptography.generate_rsa_key_pair(key_size=4096)
    keys[KEY_NAMES["TASKS_OUTPUTS_RSA_PRIVATE_KEY"]] = rsa_private_key.decode('utf-8')
    keys[KEY_NAMES["TASKS_OUTPUTS_RSA_PUBLIC_KEY"]] = rsa_public_key.decode('utf-8')
    
    print("Generating ECDSA key pair for task outputs...")
    ecdsa_private_key, ecdsa_public_key = cryptography.generate_ecdsa_key_pair()
    keys[KEY_NAMES["TASKS_OUTPUTS_ECDSA_PRIVATE_KEY"]] = ecdsa_private_key.decode('utf-8')
    keys[KEY_NAMES["TASKS_OUTPUTS_ECDSA_PUBLIC_KEY"]] = ecdsa_public_key.decode('utf-8')
    
    with open(keys_file_path, 'w', encoding='utf-8') as f:
        json.dump(keys, f, indent=2)
    
    print(f"Keys successfully saved to {keys_file_path}")
    return keys


def load_keys(keys_file_path: str = DEFAULT_KEYS_FILE) -> Dict[str, str]:
    if not os.path.exists(keys_file_path):
        raise FileNotFoundError(f"Keys file not found at {keys_file_path}. Run generate_and_save_keys() first.")
    
    with open(keys_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def set_keys_in_settings(keys_file_path: str = DEFAULT_KEYS_FILE) -> None:
    from octobot_node.app.core.config import settings
    
    keys = load_keys(keys_file_path)
    
    def to_bytes(key_value: str) -> bytes:
        if isinstance(key_value, bytes):
            return key_value
        return key_value.encode('utf-8') if key_value else None
    
    settings.TASKS_INPUTS_RSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_RSA_PUBLIC_KEY"]))
    settings.TASKS_INPUTS_RSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_RSA_PRIVATE_KEY"]))
    settings.TASKS_INPUTS_ECDSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_ECDSA_PUBLIC_KEY"]))
    settings.TASKS_INPUTS_ECDSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_ECDSA_PRIVATE_KEY"]))
    
    settings.TASKS_OUTPUTS_RSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_RSA_PUBLIC_KEY"]))
    settings.TASKS_OUTPUTS_RSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_RSA_PRIVATE_KEY"]))
    settings.TASKS_OUTPUTS_ECDSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_ECDSA_PUBLIC_KEY"]))
    settings.TASKS_OUTPUTS_ECDSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_ECDSA_PRIVATE_KEY"]))
    
    print("Keys successfully loaded into settings")


def encrypt_csv_content(
    csv_rows: List[Dict[str, str]],
    content_column: str = "content"
) -> List[Dict[str, str]]:
    from octobot_node.app.core.config import settings
    
    if settings.TASKS_INPUTS_RSA_PUBLIC_KEY is None or settings.TASKS_INPUTS_ECDSA_PRIVATE_KEY is None:
        raise ValueError(
            f"Encryption keys are not set in settings. "
            f"TASKS_INPUTS_RSA_PUBLIC_KEY={settings.TASKS_INPUTS_RSA_PUBLIC_KEY is not None}, "
            f"TASKS_INPUTS_ECDSA_PRIVATE_KEY={settings.TASKS_INPUTS_ECDSA_PRIVATE_KEY is not None}. "
            f"Call set_keys_in_settings() or provide keys to merge_and_encrypt_csv() first."
        )
    
    encrypted_rows: List[Dict[str, str]] = []
    
    for row in csv_rows:
        encrypted_row = row.copy()
        content = row.get(content_column, "")
        
        if content:
            try:
                encrypted_content, metadata = encrypt_task_content(content)
                encrypted_row[content_column] = encrypted_content
                encrypted_row["metadata"] = metadata
            except Exception as e:
                error_msg = f"Failed to encrypt content for row '{row.get('name', 'unknown')}': {e}"
                raise Exception(error_msg) from e
        else:
            encrypted_row["metadata"] = ""
        
        encrypted_rows.append(encrypted_row)
    
    return encrypted_rows


def decrypt_csv_content(
    csv_rows: List[Dict[str, str]],
    content_column: str = "content",
    metadata_column: str = "metadata"
) -> List[Dict[str, str]]:
    decrypted_rows: List[Dict[str, str]] = []
    
    for row in csv_rows:
        decrypted_row = row.copy()
        encrypted_content = row.get(content_column, "")
        metadata = row.get(metadata_column, "")
        
        if encrypted_content and metadata:
            try:
                decrypted_content = decrypt_task_content(encrypted_content, metadata)
                decrypted_row[content_column] = decrypted_content
            except Exception as e:
                print(f"Failed to decrypt content for row '{row.get('name', 'unknown')}': {e}")
        elif not encrypted_content:
            pass
        else:
            print(f"Warning: Row '{row.get('name', 'unknown')}' has content but no metadata. Skipping decryption.")
        
        decrypted_row.pop(metadata_column, None)
        decrypted_rows.append(decrypted_row)
    
    return decrypted_rows


def encrypt_csv_file(
    input_file_path: str,
    output_file_path: str,
    content_column: str = "content"
) -> None:
    rows = parse_csv(input_file_path)
    encrypted_rows = encrypt_csv_content(rows, content_column)
    headers = ["name", content_column, "type", "metadata"]
    
    with open(output_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in encrypted_rows:
            writer.writerow([
                row.get("name", ""),
                row.get(content_column, ""),
                row.get("type", ""),
                row.get("metadata", "")
            ])


def decrypt_csv_file(
    input_file_path: str,
    output_file_path: str,
    content_column: str = "content",
    metadata_column: str = "metadata"
) -> None:
    rows = []
    with open(input_file_path, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(dict(row))
    decrypted_rows = decrypt_csv_content(rows, content_column, metadata_column)
    headers = ["name", content_column, "type"]
    
    with open(output_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for row in decrypted_rows:
            writer.writerow([
                row.get("name", ""),
                row.get(content_column, ""),
                row.get("type", "")
            ])


def merge_and_encrypt_csv(
    input_file_path: str,
    output_file_path: str,
    content_column: str = "content",
    keys: Optional[Dict[str, str]] = None,
    keys_file_path: Optional[str] = None
) -> None:
    if keys_file_path:
        set_keys_in_settings(keys_file_path)
    elif keys:
        from octobot_node.app.core.config import settings
        
        def to_bytes(key_value: str) -> bytes:
            if isinstance(key_value, bytes):
                return key_value
            return key_value.encode('utf-8') if key_value else None
        
        settings.TASKS_INPUTS_RSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_RSA_PUBLIC_KEY"]))
        settings.TASKS_INPUTS_RSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_RSA_PRIVATE_KEY"]))
        settings.TASKS_INPUTS_ECDSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_ECDSA_PUBLIC_KEY"]))
        settings.TASKS_INPUTS_ECDSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_INPUTS_ECDSA_PRIVATE_KEY"]))
        settings.TASKS_OUTPUTS_RSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_RSA_PUBLIC_KEY"]))
        settings.TASKS_OUTPUTS_RSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_RSA_PRIVATE_KEY"]))
        settings.TASKS_OUTPUTS_ECDSA_PUBLIC_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_ECDSA_PUBLIC_KEY"]))
        settings.TASKS_OUTPUTS_ECDSA_PRIVATE_KEY = to_bytes(keys.get(KEY_NAMES["TASKS_OUTPUTS_ECDSA_PRIVATE_KEY"]))
    
    rows = parse_csv(input_file_path)
    encrypted_rows = encrypt_csv_content(rows, content_column)
    headers = ["name", content_column, "type", "metadata"]
    
    with open(output_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in encrypted_rows:
            writer.writerow([
                row.get("name", ""),
                row.get(content_column, ""),
                row.get("type", ""),
                row.get("metadata", "")
            ])
