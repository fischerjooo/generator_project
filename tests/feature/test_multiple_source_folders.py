#!/usr/bin/env python3
"""
Multiple Source Folders tests.

Comprehensive test suite for verifying the functionality of
multiple source folders components.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.config import Config
from c_to_plantuml.main import main
from c_to_plantuml.parser import Parser
from tests.feature.base import BaseFeatureTest


class TestMultipleSourceFolders(BaseFeatureTest):
    """Test cases for multiple source folders functionality within a single project"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        self.source_folder1 = os.path.join(self.temp_dir, "src1")
        self.source_folder2 = os.path.join(self.temp_dir, "src2")
        self.source_folder3 = os.path.join(self.temp_dir, "src3")

        # Create source folder directories
        os.makedirs(self.source_folder1, exist_ok=True)
        os.makedirs(self.source_folder2, exist_ok=True)
        os.makedirs(self.source_folder3, exist_ok=True)

        # Create test files in each source folder
        self._create_test_files()

    def tearDown(self):
        """Clean up test fixtures"""
        super().tearDown()

    def _create_test_files(self):
        """Create test C files in each source folder"""
        # Source folder 1: Basic structures
        src1_main = os.path.join(self.source_folder1, "main.c")
        with open(src1_main, "w") as f:
            f.write(
                """
#include "utils.h"

struct Person {
    char name[50];
    int age;
};

int main() {
    struct Person p = {"John", 30};
    return 0;
}
"""
            )

        src1_utils = os.path.join(self.source_folder1, "utils.h")
        with open(src1_utils, "w") as f:
            f.write(
                """
#ifndef UTILS_H
#define UTILS_H

typedef struct {
    int x, y;
} Point;

void print_point(Point p);

#endif
"""
            )

        # Source folder 2: Enums and functions
        src2_main = os.path.join(self.source_folder2, "app.c")
        with open(src2_main, "w") as f:
            f.write(
                """
#include "types.h"

enum Color {
    RED,
    GREEN,
    BLUE
};

void process_color(enum Color c) {
    // Process color
}
"""
            )

        src2_types = os.path.join(self.source_folder2, "types.h")
        with open(src2_types, "w") as f:
            f.write(
                """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned int uint32_t;
typedef struct {
    uint32_t id;
    char name[100];
} Item;

#endif
"""
            )

        # Source folder 3: Complex structures
        src3_main = os.path.join(self.source_folder3, "complex.c")
        with open(src3_main, "w") as f:
            f.write(
                """
#include "data.h"

union Data {
    int i;
    float f;
    char str[20];
};

struct Container {
    union Data data;
    int type;
};
"""
            )

        src3_data = os.path.join(self.source_folder3, "data.h")
        with open(src3_data, "w") as f:
            f.write(
                """
#ifndef DATA_H
#define DATA_H

#define MAX_SIZE 100

typedef struct {
    int values[MAX_SIZE];
    int count;
} Array;

#endif
"""
            )

    def create_config_file(self, source_folders):
        """Create a configuration file with specified source folders"""
        config_data = {
            "project_name": "multi_source_test",
            "source_folders": source_folders,
            "output_dir": os.path.join(self.temp_dir, "output"),
            "recursive_search": True,
            "include_depth": 1,
        }

        config_path = os.path.join(self.temp_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        return config_path

    def test_multiple_source_folders_parsing(self):
        """Test that multiple source folders are parsed correctly"""
        config_path = self.create_config_file(
            [self.source_folder1, self.source_folder2, self.source_folder3]
        )

        # Load config to verify it's correct
        config = Config.load(config_path)
        self.assertEqual(len(config.source_folders), 3)
        self.assertEqual(config.source_folders[0], self.source_folder1)
        self.assertEqual(config.source_folders[1], self.source_folder2)
        self.assertEqual(config.source_folders[2], self.source_folder3)

    def test_parser_multiple_source_folders_method(self):
        """Test the parse method with multiple source folders"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "combined_model.json")

        # Test with multiple source folders
        result = parser.parse(
            project_root=[
                self.source_folder1,
                self.source_folder2,
                self.source_folder3,
            ],
            output_file=output_file,
            recursive_search=True,
        )

        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

        # Load and verify the combined model
        with open(output_file, "r") as f:
            model_data = json.load(f)

        # Check that files from all source folders are included
        files = model_data.get("files", {})
        self.assertGreater(len(files), 0)

        # Check for files from each source folder
        src1_files = [f for f in files.keys() if f.startswith("src1_")]
        src2_files = [f for f in files.keys() if f.startswith("src2_")]
        src3_files = [f for f in files.keys() if f.startswith("src3_")]

        self.assertGreater(len(src1_files), 0)
        self.assertGreater(len(src2_files), 0)
        self.assertGreater(len(src3_files), 0)

        # Verify specific files are present
        self.assertTrue(any("main.c" in f for f in src1_files))
        self.assertTrue(any("app.c" in f for f in src2_files))
        self.assertTrue(any("complex.c" in f for f in src3_files))

    def test_single_source_folder_backward_compatibility(self):
        """Test that single source folder still works (backward compatibility)"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "single_model.json")

        # Test with single source folder (string parameter for backward compatibility)
        result = parser.parse(
            project_root=self.source_folder1,
            output_file=output_file,
            recursive_search=True,
        )

        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

        # Load and verify the model
        with open(output_file, "r") as f:
            model_data = json.load(f)

        files = model_data.get("files", {})
        self.assertGreater(len(files), 0)

        # Check that files are present without source folder prefix
        self.assertTrue(any("main.c" in f for f in files.keys()))

    def test_empty_source_folders_error(self):
        """Test that empty source_folders list raises an error"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "error_model.json")

        with self.assertRaises(ValueError):
            parser.parse(
                project_root=[], output_file=output_file, recursive_search=True
            )

    def test_invalid_source_folder_error(self):
        """Test that invalid source folder raises an error"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "error_model.json")

        with self.assertRaises(Exception):  # Should raise some kind of error
            parser.parse(
                project_root=["/nonexistent/path"],
                output_file=output_file,
                recursive_search=True,
            )

    def test_multiple_source_folders_with_config(self):
        """Test multiple source folders with configuration and filters"""
        config_path = self.create_config_file(
            [self.source_folder1, self.source_folder2]
        )

        config = Config.load(config_path)

        # Add some filters to test they work with multiple source folders
        config.file_filters = {"include": [".*\\.c$", ".*\\.h$"]}

        parser = Parser()
        output_file = os.path.join(self.temp_dir, "filtered_model.json")

        result = parser.parse(
            project_root=config.source_folders,
            output_file=output_file,
            recursive_search=config.recursive_search,
            config=config,
        )

        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_source_folder_name_collision_handling(self):
        """Test that files with same names from different source folders are handled correctly"""
        # Create a file with the same name in different source folders
        same_name_file1 = os.path.join(self.source_folder1, "common.h")
        same_name_file2 = os.path.join(self.source_folder2, "common.h")

        with open(same_name_file1, "w") as f:
            f.write("#ifndef COMMON1_H\n#define COMMON1_H\nint src1_var;\n#endif\n")

        with open(same_name_file2, "w") as f:
            f.write("#ifndef COMMON2_H\n#define COMMON2_H\nint src2_var;\n#endif\n")

        parser = Parser()
        output_file = os.path.join(self.temp_dir, "collision_model.json")

        result = parser.parse(
            project_root=[self.source_folder1, self.source_folder2],
            output_file=output_file,
            recursive_search=True,
        )

        self.assertEqual(result, output_file)

        # Load and verify both files are present with different keys
        with open(output_file, "r") as f:
            model_data = json.load(f)

        files = model_data.get("files", {})

        # Check that both common.h files are present with source folder prefixes
        src1_common = [
            f for f in files.keys() if f.startswith("src1_") and "common.h" in f
        ]
        src2_common = [
            f for f in files.keys() if f.startswith("src2_") and "common.h" in f
        ]

        self.assertEqual(len(src1_common), 1)
        self.assertEqual(len(src2_common), 1)
        self.assertNotEqual(src1_common[0], src2_common[0])

    def test_project_name_from_config(self):
        """Test that project name is taken from configuration"""
        config_path = self.create_config_file(
            [self.source_folder1, self.source_folder2]
        )

        config = Config.load(config_path)
        config.project_name = "TestProject"

        parser = Parser()
        output_file = os.path.join(self.temp_dir, "named_model.json")

        result = parser.parse(
            project_root=config.source_folders,
            output_file=output_file,
            recursive_search=True,
            config=config,
        )

        self.assertEqual(result, output_file)

        # Load and verify the project name is correct
        with open(output_file, "r") as f:
            model_data = json.load(f)

        self.assertEqual(model_data.get("project_name"), "TestProject")


if __name__ == "__main__":
    unittest.main()
