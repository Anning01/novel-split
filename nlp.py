#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2024/12/02 01:47
# @file:nlp.py
import argparse
import re
import os
import shutil
from transformers import pipeline
from chinese2digit import chinese2digit as c2d
import chardet


# Define file encoding
def detect_file_encoding(input_file):
    with open(input_file, 'rb') as f:
        text = f.read()
        res = chardet.detect(text)
        encoding = res['encoding']
    return encoding


FILE_ENCODING = 'utf-8'


# Small language model to perform chapter identification
def load_nlp_model():
    # Load a small, efficient NLP model for text classification
    # Using "transformers" pipeline with a zero-shot classification model
    # To minimize memory usage, select a small pre-trained model such as "distilbert"
    classifier = pipeline('zero-shot-classification', model="typeform/distilbert-base-uncased-mnli")
    return classifier


def processing_priority(line, instance_index=0):
    my_pattern = Pattern()

    if instance_index == 0:
        chapter_match_ = re.search(my_pattern.get_digit_number_from_chapter(), line)
        if not chapter_match_:
            chapter_match_ = re.search(my_pattern.get_chinese_number_from_chapter(), line)
            instance_index = 1
            current_chapter_match = c2d(chapter_match_[0])
        else:
            current_chapter_match = chapter_match_[0]
        return current_chapter_match, instance_index
    else:
        chapter_match_ = re.search(my_pattern.get_chinese_number_from_chapter(), line)
        if not chapter_match_:
            chapter_match_ = re.search(my_pattern.get_digit_number_from_chapter(), line)
            instance_index = 0
            current_chapter_match = chapter_match_[0]
        else:
            current_chapter_match = c2d(chapter_match_[0])
        return current_chapter_match, instance_index


def split_txt_index_nlp(input_file, output_path, classifier) -> None:
    print("开始使用 NLP 技术拆分 TXT 文件")
    if not os.path.exists(os.path.join(output_path, "temp")):
        os.makedirs(os.path.join(output_path, "temp"))
    else:
        shutil.rmtree(os.path.join(output_path, "temp"))
        os.makedirs(os.path.join(output_path, "temp"))

    save_file = None
    chapter_index = 0  # Chapter index for sequential verification
    instance_index = 0
    my_pattern = Pattern()

    FILE_ENCODING = detect_file_encoding(input_file)
    with open(input_file, encoding=FILE_ENCODING) as f:
        lines = f.readlines()
        seen_chapters = set()
        for i, line in enumerate(lines):
            line = line.rstrip('\r\n')
            chapter_candidate = re.search(my_pattern.get_global_pattern(), line)
            if chapter_candidate:
                result = classifier(line, candidate_labels=["Chapter", "Not Chapter"])
                chapter_score = result['scores'][0] if result['labels'][0] == "Chapter" else 0
                sequential_bonus = 0

                current_chapter_match, instance_index = processing_priority(line, instance_index)

                if current_chapter_match == chapter_index + 1:
                    sequential_bonus = 0.1  # Give a small boost for correct sequential order
                final_score = chapter_score + sequential_bonus

                print(result['labels'][0])
                print(final_score)
                # Check if it has been classified as "Chapter"
                if final_score > 0.7:
                    print(f"找到章节标题: {line}")
                    chapter = current_chapter_match
                    chapter_index = chapter  # Update the expected chapter index

                    if chapter in seen_chapters:
                        continue
                    seen_chapters.add(chapter)

                    # Find new Chapter
                    if save_file is not None:
                        save_file.close()
                    save_file_path = os.path.join(output_path, "temp")
                    save_file_path = os.path.join(save_file_path, f"{chapter}.txt")
                    save_file = open(save_file_path, mode='a', encoding=FILE_ENCODING)
                    save_file.write(line + "\n")
                else:
                    # Line was not classified as chapter heading
                    if save_file is not None:
                        save_file.write(line + "\n")
            else:
                if save_file is not None:
                    save_file.write(line + "\n")

    if save_file is not None:
        save_file.close()


def split_txt_title_nlp(input_file, output_path, classifier) -> None:
    print("开始使用 NLP 技术拆分 TXT 文件")
    if not os.path.exists(os.path.join(output_path, "temp")):
        os.makedirs(os.path.join(output_path, "temp"))
    else:
        shutil.rmtree(os.path.join(output_path, "temp"))
        os.makedirs(os.path.join(output_path, "temp"))

    save_file = None
    chapter_index = 0  # Chapter index for sequential verification
    instance_index = 0
    my_pattern = Pattern()

    FILE_ENCODING = detect_file_encoding(input_file)
    with open(input_file, encoding=FILE_ENCODING) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = line.rstrip('\r\n')
            chapter_candidate = re.search(my_pattern.get_global_pattern(), line)
            if chapter_candidate:
                chapter = chapter_candidate[0] + line.split(chapter_candidate[0])[-1]
                result = classifier(line, candidate_labels=["Chapter", "Not Chapter"])
                chapter_score = result['scores'][0] if result['labels'][0] == "Chapter" else 0
                sequential_bonus = 0
                # Extract chapter number for sequential verification

                current_chapter_match, instance_index = processing_priority(line, instance_index)

                # Apply sequential bonus if chapter index is in expected order
                if current_chapter_match == chapter_index + 1:
                    sequential_bonus = 0.1  # Give a small boost for correct sequential order

                    # Final score calculation
                final_score = chapter_score + sequential_bonus

                # print(result['labels'][0])
                # print(final_score)
                # Check if it has been classified as "Chapter"
                if final_score > 0.7:
                    print(f"找到章节标题: {chapter}")
                    chapter_index += 1  # Update the expected chapter index
                    # Find new Chapter
                    if save_file is not None:
                        save_file.close()
                    save_file_path = os.path.join(output_path, "temp")
                    save_file_path = os.path.join(save_file_path, f"{chapter_index}{chapter}.txt")
                    save_file = open(save_file_path, mode='a', encoding=FILE_ENCODING)
                    save_file.write(line + "\n")
                else:
                    # Line was not classified as chapter heading
                    if save_file is not None:
                        save_file.write(line + "\n")
            else:
                if save_file is not None:
                    save_file.write(line + "\n")

    if save_file is not None:
        save_file.close()


class Pattern:
    """
    This is the base class for pattern generation.
    """

    def __init__(self) -> None:
        # self.prefix = r"第章回部节集卷"
        self.prefix = r"第"
        self.body = r"\d一二三四五六七八九十零〇百千两"
        self.suffix = r"第章回部节集卷"
        self.tail = r' |、|，|\S'
        self.interval = r" *"
        self.digit_rule = r"\d"
        self.chinese_rule = r"一二三四五六七八九十零〇百千两"

    def get_global_pattern(self) -> str:
        """
        This pattern is used to grab chapter name from txt.
        :return: pattern
        """
        pattern = r"[" + self.prefix + r"]"
        pattern = pattern + self.interval
        pattern = pattern + r"[" + self.body + r"]" + "+"
        pattern = pattern + self.interval
        pattern = pattern + r"[" + self.suffix + r"]"
        pattern = pattern + r"(" + self.tail + r")"

        return pattern

    def get_digit_number_from_chapter(self) -> str:
        """
        This function will return the pattern to grab chapter index from txt.
        :return:
        """
        pattern = r"[" + self.digit_rule + r"]" + "+"

        return pattern

    def get_chinese_number_from_chapter(self) -> str:
        """
        This function will return
        :return:
        """
        pattern = r"[" + self.chinese_rule + r"]" + "+"

        return pattern


if __name__ == '__main__':
    classifier = load_nlp_model()
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help='input file path')
    parser.add_argument('--output', type=str, help='output folder path')
    args = parser.parse_args()
    input_file = args.input
    output_path = args.output
    split_txt_title_nlp(input_file=input_file, output_path=output_path, classifier=classifier)

