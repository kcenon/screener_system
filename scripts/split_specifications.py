#!/usr/bin/env python3
"""
Split large specification documents (PRD, SRS, SDS) into smaller, manageable files
for the Docusaurus documentation site.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


def create_frontmatter(doc_id: str, title: str, description: str,
                       sidebar_label: str, position: int, tags: List[str]) -> str:
    """Create Docusaurus frontmatter metadata."""
    tags_yaml = '\n  - '.join(tags)
    return f"""---
id: {doc_id}
title: {title}
description: {description}
sidebar_label: {sidebar_label}
sidebar_position: {position}
tags:
  - {tags_yaml}
---

"""


def create_navigation_box(files: List[Tuple[str, str]], current_idx: int) -> str:
    """Create navigation info box for inter-document linking."""
    nav_items = []
    for i, (filename, label) in enumerate(files):
        if i == current_idx:
            nav_items.append(f"- [{label}]({filename}) (Current)")
        else:
            nav_items.append(f"- [{label}]({filename})")

    nav_text = '\n'.join(nav_items)
    return f""":::info Navigation
{nav_text}
:::

"""


def split_prd(source_path: Path, target_dir: Path):
    """Split PRD.md into 4 logical sections."""
    print("Splitting PRD.md...")

    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define split points and metadata
    sections = [
        {
            'filename': 'overview.md',
            'title': 'PRD - Overview',
            'description': 'Executive summary, product vision, and market analysis',
            'sidebar_label': 'Overview',
            'position': 1,
            'start_section': '## 1. Executive Summary',
            'end_section': '## 4. User Personas',
        },
        {
            'filename': 'users-features.md',
            'title': 'PRD - Users & Features',
            'description': 'User personas, use cases, and feature requirements',
            'sidebar_label': 'Users & Features',
            'position': 2,
            'start_section': '## 4. User Personas',
            'end_section': '## 6. Technical Requirements',
        },
        {
            'filename': 'technical.md',
            'title': 'PRD - Technical',
            'description': 'Technical and data requirements',
            'sidebar_label': 'Technical',
            'position': 3,
            'start_section': '## 6. Technical Requirements',
            'end_section': '## 8. UI/UX Requirements',
        },
        {
            'filename': 'implementation.md',
            'title': 'PRD - Implementation',
            'description': 'UI/UX, success metrics, roadmap, and risk analysis',
            'sidebar_label': 'Implementation',
            'position': 4,
            'start_section': '## 8. UI/UX Requirements',
            'end_section': None,  # Till end
        },
    ]

    nav_files = [(s['filename'], s['sidebar_label']) for s in sections]

    for idx, section in enumerate(sections):
        # Extract section content
        start_idx = content.find(section['start_section'])
        if start_idx == -1:
            print(f"  Warning: Could not find start section: {section['start_section']}")
            continue

        if section['end_section']:
            end_idx = content.find(section['end_section'], start_idx + 1)
            if end_idx == -1:
                section_content = content[start_idx:]
            else:
                section_content = content[start_idx:end_idx]
        else:
            section_content = content[start_idx:]

        # Create file with frontmatter and navigation
        frontmatter = create_frontmatter(
            f"prd-{section['filename'].replace('.md', '')}",
            section['title'],
            section['description'],
            section['sidebar_label'],
            section['position'],
            ['specification', 'product', 'requirements']
        )

        navigation = create_navigation_box(nav_files, idx)

        # Fix HTML tags for MDX
        section_content = re.sub(r'<br>', '<br />', section_content)
        section_content = re.sub(r'<hr>', '<hr />', section_content)

        output_path = target_dir / section['filename']
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(navigation)
            f.write(f"# Product Requirements Document - {section['sidebar_label']}\n\n")
            f.write(section_content.strip())

        print(f"  Created: {output_path.name}")


def split_srs(source_path: Path, target_dir: Path):
    """Split SRS.md into 3 logical sections."""
    print("Splitting SRS.md...")

    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = [
        {
            'filename': 'introduction.md',
            'title': 'SRS - Introduction & Overview',
            'description': 'Software requirements specification introduction and overall description',
            'sidebar_label': 'Introduction',
            'position': 1,
            'start_section': '## 1. Introduction',
            'end_section': '## 3. Specific Requirements',
        },
        {
            'filename': 'requirements.md',
            'title': 'SRS - Requirements & Features',
            'description': 'Functional requirements, external interfaces, and system features',
            'sidebar_label': 'Requirements',
            'position': 2,
            'start_section': '## 3. Specific Requirements',
            'end_section': '## 6. Non-Functional Requirements',
        },
        {
            'filename': 'nonfunctional-other.md',
            'title': 'SRS - Non-Functional & Other',
            'description': 'Non-functional requirements, legal requirements, and appendices',
            'sidebar_label': 'Non-Functional',
            'position': 3,
            'start_section': '## 6. Non-Functional Requirements',
            'end_section': None,
        },
    ]

    nav_files = [(s['filename'], s['sidebar_label']) for s in sections]

    for idx, section in enumerate(sections):
        start_idx = content.find(section['start_section'])
        if start_idx == -1:
            print(f"  Warning: Could not find start section: {section['start_section']}")
            continue

        if section['end_section']:
            end_idx = content.find(section['end_section'], start_idx + 1)
            section_content = content[start_idx:end_idx] if end_idx != -1 else content[start_idx:]
        else:
            section_content = content[start_idx:]

        frontmatter = create_frontmatter(
            f"srs-{section['filename'].replace('.md', '')}",
            section['title'],
            section['description'],
            section['sidebar_label'],
            section['position'],
            ['specification', 'requirements', 'software']
        )

        navigation = create_navigation_box(nav_files, idx)

        # Fix HTML tags and special characters
        section_content = re.sub(r'<br>', '<br />', section_content)
        section_content = re.sub(r'<(\d)', r'&lt;\1', section_content)  # Fix <9 → &lt;9
        section_content = re.sub(r'>(\d)', r'&gt;\1', section_content)  # Fix >9 → &gt;9

        output_path = target_dir / section['filename']
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(navigation)
            f.write(f"# Software Requirements Specification - {section['sidebar_label']}\n\n")
            f.write(section_content.strip())

        print(f"  Created: {output_path.name}")


def split_sds(source_path: Path, target_dir: Path):
    """Split SDS.md into 10 logical sections."""
    print("Splitting SDS.md...")

    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = [
        ('introduction.md', 'Introduction', '## 1. Introduction', '## 2. System Architecture', 1),
        ('system-architecture.md', 'System Architecture', '## 2. System Architecture', '## 3. Component Design', 2),
        ('component-design.md', 'Component Design', '## 3. Component Design', '## 4. Database Design', 3),
        ('database-design.md', 'Database Design', '## 4. Database Design', '## 5. API Design', 4),
        ('api-design.md', 'API Design', '## 5. API Design', '## 6. Data Pipeline Design', 5),
        ('data-pipeline.md', 'Data Pipeline', '## 6. Data Pipeline Design', '## 7. Security Design', 6),
        ('security-design.md', 'Security Design', '## 7. Security Design', '## 8. Performance Design', 7),
        ('performance-design.md', 'Performance Design', '## 8. Performance Design', '## 9. Deployment Architecture', 8),
        ('deployment.md', 'Deployment', '## 9. Deployment Architecture', '## 10. Technology Stack', 9),
        ('tech-stack-decisions.md', 'Tech Stack & Decisions', '## 10. Technology Stack', None, 10),
    ]

    nav_files = [(s[0], s[1]) for s in sections]

    for idx, (filename, label, start_sec, end_sec, position) in enumerate(sections):
        start_idx = content.find(start_sec)
        if start_idx == -1:
            print(f"  Warning: Could not find start section: {start_sec}")
            continue

        if end_sec:
            end_idx = content.find(end_sec, start_idx + 1)
            section_content = content[start_idx:end_idx] if end_idx != -1 else content[start_idx:]
        else:
            section_content = content[start_idx:]

        frontmatter = create_frontmatter(
            f"sds-{filename.replace('.md', '')}",
            f"SDS - {label}",
            f"Software design specification - {label.lower()}",
            label,
            position,
            ['specification', 'design', 'architecture']
        )

        navigation = create_navigation_box(nav_files, idx)

        # Fix HTML tags and special characters
        section_content = re.sub(r'<br>', '<br />', section_content)
        section_content = re.sub(r'<hr>', '<hr />', section_content)
        section_content = re.sub(r'<(\d)', r'&lt;\1', section_content)
        section_content = re.sub(r'>(\d)', r'&gt;\1', section_content)

        output_path = target_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(navigation)
            f.write(f"# Software Design Specification - {label}\n\n")
            f.write(section_content.strip())

        print(f"  Created: {output_path.name}")


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent

    # Define paths
    docs_dir = project_root / 'docs'
    target_base = project_root / 'docs-site' / 'docs' / '05-specifications'

    # Ensure target directories exist
    prd_dir = target_base / 'prd'
    srs_dir = target_base / 'srs'
    sds_dir = target_base / 'sds'

    prd_dir.mkdir(parents=True, exist_ok=True)
    srs_dir.mkdir(parents=True, exist_ok=True)
    sds_dir.mkdir(parents=True, exist_ok=True)

    # Split documents
    split_prd(docs_dir / 'PRD.md', prd_dir)
    split_srs(docs_dir / 'SRS.md', srs_dir)
    split_sds(docs_dir / 'SDS.md', sds_dir)

    print("\n✅ All specification documents split successfully!")


if __name__ == '__main__':
    main()
