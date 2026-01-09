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
from pathlib import Path

from octobot_node.tools.csv_utils import (
    generate_and_save_keys,
    parse_csv,
    merge_csv_columns,
    DEFAULT_KEYS_FILE,
    encrypt_result_csv_file,
    decrypt_result_csv_file,
)
from octobot_node.tools.encrypt_csv_tasks import encrypt_csv_file_from_keys_file
from octobot_node.tools.decrypt_csv_tasks import decrypt_csv_file_from_keys_file


class TestCSVEncryption:
    def test_encrypt_and_decrypt_csv(self, tmp_path: Path) -> None:
        test_dir = Path(__file__).parent
        test_csv_path = test_dir / "test-tasks.csv"
        keys_file = str(test_dir / DEFAULT_KEYS_FILE)
        
        encrypted_csv = test_dir / "encrypted_tasks.csv"
        decrypted_csv = tmp_path / "decrypted_tasks.csv"
        merged_csv = tmp_path / "merged_tasks.csv"
        
        generate_and_save_keys(keys_file)
        
        merge_csv_columns(str(test_csv_path), str(merged_csv))
        
        encrypt_csv_file_from_keys_file(
            input_file_path=str(test_csv_path),
            output_file_path=str(encrypted_csv),
            keys_file_path=keys_file
        )
        
        assert encrypted_csv.exists(), "Encrypted CSV file should be created"
        
        decrypt_csv_file_from_keys_file(
            input_file_path=str(encrypted_csv),
            output_file_path=str(decrypted_csv),
            keys_file_path=keys_file
        )
        
        assert decrypted_csv.exists(), "Decrypted CSV file should be created"
        
        original_rows = parse_csv(str(merged_csv))
        decrypted_rows = parse_csv(str(decrypted_csv))
        
        assert len(original_rows) == len(decrypted_rows), "Number of rows should match"
        
        for original_row, decrypted_row in zip(original_rows, decrypted_rows):
            assert original_row["name"] == decrypted_row["name"], "Names should match"
            assert original_row["type"] == decrypted_row["type"], "Types should match"
            assert original_row["content"] == decrypted_row["content"], "Content should match after decryption"

    def test_decrypt_exported_result_csv(self, tmp_path: Path) -> None:
        test_dir = Path(__file__).parent
        keys_file = str(test_dir / DEFAULT_KEYS_FILE)
        
        # Generate keys (same way as test_encrypt_and_decrypt_csv)
        generate_and_save_keys(keys_file)
        
        # Set keys in settings
        from octobot_node.app.core.config import settings
        from octobot_node.tools.csv_utils import set_keys_in_settings
        set_keys_in_settings(keys_file)
        
        assert settings.TASKS_OUTPUTS_RSA_PUBLIC_KEY is not None, "RSA public key should be set"
        assert settings.TASKS_OUTPUTS_ECDSA_PRIVATE_KEY is not None, "ECDSA private key should be set"
        assert settings.TASKS_OUTPUTS_RSA_PRIVATE_KEY is not None, "RSA private key should be set"
        assert settings.TASKS_OUTPUTS_ECDSA_PUBLIC_KEY is not None, "ECDSA public key should be set"
        
        # Create a test result CSV file (save to test directory for reference)
        original_result_csv = test_dir / "test-results.csv"
        encrypted_result_csv = test_dir / "encrypted_results.csv"
        decrypted_result_csv = tmp_path / "decrypted_results.csv"
        
        # Create test data with results
        test_results = [
            {"name": "Task 1", "result": json.dumps({"status": "completed", "data": "result1"})},
            {"name": "Task 2", "result": json.dumps({"status": "completed", "data": "result2"})},
            {"name": "Task 3", "result": json.dumps({"status": "failed", "error": "test error"})},
        ]
        
        # Write original result CSV
        with open(original_result_csv, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "result"])
            writer.writeheader()
            for row in test_results:
                writer.writerow(row)
        
        # Encrypt the result CSV
        encrypt_result_csv_file(
            str(original_result_csv),
            str(encrypted_result_csv)
        )
        
        assert encrypted_result_csv.exists(), "Encrypted result CSV file should be created"
        
        # Decrypt the result CSV
        decrypt_result_csv_file(
            str(encrypted_result_csv),
            str(decrypted_result_csv)
        )
        
        assert decrypted_result_csv.exists(), "Decrypted result CSV file should be created"
        
        # Read and compare results
        original_rows = []
        with open(original_result_csv, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            original_rows = list(reader)
        
        decrypted_rows = []
        with open(decrypted_result_csv, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            decrypted_rows = list(reader)
        
        assert len(original_rows) == len(decrypted_rows), "Number of rows should match"
        
        for original_row, decrypted_row in zip(original_rows, decrypted_rows):
            assert original_row["name"] == decrypted_row["name"], "Names should match"
            original_result = json.loads(original_row["result"])
            assert "result" not in decrypted_row, "Result column should be split into separate columns"
            for key, value in original_result.items():
                assert key in decrypted_row, f"Column '{key}' should exist in decrypted row"
                decrypted_value_str = decrypted_row[key]
                if isinstance(value, (dict, list)):
                    decrypted_value = json.loads(decrypted_value_str)
                else:
                    try:
                        decrypted_value = json.loads(decrypted_value_str)
                    except (json.JSONDecodeError, ValueError):
                        decrypted_value = decrypted_value_str
                assert decrypted_value == value, f"Value for '{key}' should match: expected {value}, got {decrypted_value}"
