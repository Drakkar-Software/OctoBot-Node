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

import os
import tempfile
from pathlib import Path

import pytest

from tests.scheduler.task_import.csv_utils import (
    generate_and_save_keys,
    merge_and_encrypt_csv,
    decrypt_csv_file,
    parse_csv,
    merge_csv_columns,
)


class TestCSVEncryption:
    def test_encrypt_and_decrypt_csv(self, tmp_path: Path) -> None:
        test_dir = Path(__file__).parent
        test_csv_path = test_dir / "test-tasks.csv"
        keys_file = tmp_path / "test_keys.json"
        encrypted_csv = test_dir / "encrypted_tasks.csv"
        decrypted_csv = tmp_path / "decrypted_tasks.csv"
        merged_csv = tmp_path / "merged_tasks.csv"
        
        generate_and_save_keys(str(keys_file))
        
        merge_csv_columns(str(test_csv_path), str(merged_csv))
        
        from octobot_node.app.core.config import settings
        from tests.scheduler.task_import.csv_utils import set_keys_in_settings
        set_keys_in_settings(str(keys_file))
        
        assert settings.TASKS_INPUTS_RSA_PUBLIC_KEY is not None, "RSA public key should be set"
        assert settings.TASKS_INPUTS_ECDSA_PRIVATE_KEY is not None, "ECDSA private key should be set"
        
        merge_and_encrypt_csv(
            str(test_csv_path),
            str(encrypted_csv),
            keys_file_path=str(keys_file)
        )
        
        assert encrypted_csv.exists(), "Encrypted CSV file should be created"
        
        decrypt_csv_file(
            str(encrypted_csv),
            str(decrypted_csv)
        )
        
        assert decrypted_csv.exists(), "Decrypted CSV file should be created"
        
        original_rows = parse_csv(str(merged_csv))
        decrypted_rows = parse_csv(str(decrypted_csv))
        
        assert len(original_rows) == len(decrypted_rows), "Number of rows should match"
        
        for original_row, decrypted_row in zip(original_rows, decrypted_rows):
            assert original_row["name"] == decrypted_row["name"], "Names should match"
            assert original_row["type"] == decrypted_row["type"], "Types should match"
            assert original_row["content"] == decrypted_row["content"], "Content should match after decryption"
