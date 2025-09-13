#!/usr/bin/env python3
"""
File Organizer - Automatically organize files by type into folders
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse

FILE_CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
    'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c', '.h', '.json', '.xml', '.sql'],
    'Executables': ['.exe', '.msi', '.app', '.deb', '.rpm'],
    'Data': ['.csv', '.json', '.xml', '.sql', '.db', '.sqlite']
}

class FileOrganizer:
    def __init__(self, source_dir, destination_dir=None):
        self.source_dir = Path(source_dir)
        self.destination_dir = Path(destination_dir) if destination_dir else self.source_dir
        self.moved_files = []
        self.errors = []

    def get_file_category(self, file_path):
        """Determine the category of a file based on its extension"""
        extension = file_path.suffix.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if extension in extensions:
                return category
        return 'Others'

    def organize_files(self, dry_run=False):
        """Organize files in the source directory"""
        if not self.source_dir.exists():
            print(f"Error: Source directory '{self.source_dir}' does not exist!")
            return

        print(f"{'[DRY RUN] ' if dry_run else ''}Organizing files in: {self.source_dir}")
        print(f"Destination: {self.destination_dir}\n")

        files_to_organize = []

        # Collect all files to organize
        for item in self.source_dir.iterdir():
            if item.is_file():
                category = self.get_file_category(item)
                files_to_organize.append((item, category))

        if not files_to_organize:
            print("No files found to organize!")
            return

        # Organize files by category
        for file_path, category in files_to_organize:
            category_dir = self.destination_dir / category

            if not dry_run:
                # Create category directory if it doesn't exist
                category_dir.mkdir(exist_ok=True)

                # Generate unique filename if file already exists
                destination = category_dir / file_path.name
                if destination.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
                    destination = category_dir / new_name

                try:
                    # Move the file
                    shutil.move(str(file_path), str(destination))
                    self.moved_files.append((file_path.name, category))
                    print(f"✓ Moved: {file_path.name} → {category}/")
                except Exception as e:
                    self.errors.append((file_path.name, str(e)))
                    print(f"✗ Error moving {file_path.name}: {e}")
            else:
                print(f"Would move: {file_path.name} → {category}/")

        # Print summary
        self.print_summary(dry_run)

    def print_summary(self, dry_run=False):
        """Print organization summary"""
        print("\n" + "="*50)
        if dry_run:
            print("DRY RUN COMPLETE - No files were actually moved")
        else:
            print(f"ORGANIZATION COMPLETE")
            print(f"Files moved: {len(self.moved_files)}")
            if self.errors:
                print(f"Errors: {len(self.errors)}")
                for file_name, error in self.errors:
                    print(f"  - {file_name}: {error}")

        # Show organized categories
        if self.moved_files:
            categories = {}
            for file_name, category in self.moved_files:
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1

            print("\nFiles by category:")
            for category, count in sorted(categories.items()):
                print(f"  {category}: {count} file(s)")

def main():
    parser = argparse.ArgumentParser(description="Organize files by type into categorized folders")
    parser.add_argument("source", nargs='?', default=".", help="Source directory to organize (default: current directory)")
    parser.add_argument("-d", "--destination", help="Destination directory (default: same as source)")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be organized without moving files")

    args = parser.parse_args()

    organizer = FileOrganizer(args.source, args.destination)
    organizer.organize_files(dry_run=args.dry_run)

if __name__ == "__main__":
    main()