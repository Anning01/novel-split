#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2024/12/02 01:10
# @file:utils.py
import argparse
import os
import re
import shutil
from chinese2digit import chinese2digit as c2d
import chardet

FILE_ENCODING = 'utf-8'


def split_txt(input_file, output_path) -> None:
    print("开始拆分TXT")
    if not os.path.exists(os.path.join(output_path, "temp")):
        os.makedirs(os.path.join(output_path, "temp"))
    else:
        shutil.rmtree(os.path.join(output_path, "temp"))
        os.makedirs(os.path.join(output_path, "temp"))

    # Init 0 chapter.
    chapter = -1
    save_file_path = os.path.join(output_path, "temp")
    save_file_path = os.path.join(save_file_path, "%s.txt" % str(chapter))
    save_file = open(save_file_path, mode='a', encoding='utf-8')

    my_pattern = Pattern()
    global FILE_ENCODING
    FILE_ENCODING = detect_file_encoding(input_file)
    with open(input_file, encoding=FILE_ENCODING) as f:
        while True:
            # Read one line from
            line = f.readline()
            if not line:
                save_file.close()
                break
            line = line.rstrip('\r\n')

            # pattern = r'[第章回部节集卷] *[\d一二三四五六七八九十零〇百千两]+ *[第章回部节集卷]( |、)'
            chapter_org = re.search(my_pattern.get_global_pattern(), line)
            if chapter_org is not None:
                print("找到：%s" % str(chapter_org[0]) + "\n")
                chapter = re.search(my_pattern.get_digit_number_from_chapter(), chapter_org[0])
                if not chapter:
                    chapter = re.search(my_pattern.get_chinese_number_from_chapter(), chapter_org[0])
                    chapter = c2d(chapter[0])
                else:
                    chapter = chapter[0]
                print(chapter)
                # Find new Chapter
                if save_file is not None:
                    save_file.close()

                save_file_path = os.path.join(output_path, "temp")
                save_file_path = os.path.join(save_file_path, "%s.txt" % str(chapter))
                save_file = open(save_file_path, mode='a', encoding=FILE_ENCODING)
                save_file.write(line)
                save_file.write("\n")
            else:
                save_file.write(line)
                save_file.write("\n")


def join_txt(txt_store_path, final_txt_path) -> None:
    print("开始排序并合并")
    if not os.path.exists(final_txt_path):
        os.makedirs(final_txt_path)

    txt_name = []

    # Get txt names
    for root, dirs, files in os.walk(txt_store_path, topdown=False):  # pylint: disable=unused-variable
        for name in files:
            txt_name.append(name.split(".")[0])
    txt_name = [int(i) for i in txt_name]
    txt_name.sort(reverse=False)
    txt_name = [str(i) for i in txt_name]
    print("排序完成，共 %d 章！" % int(len(txt_name)) + "\n")
    txt_out = os.path.join(final_txt_path, "output.txt")

    with open(txt_out, mode='a', encoding=FILE_ENCODING) as f:
        for each in txt_name:
            print("开始加入: %s" % each + ".txt" + "\n")
            txt_path = os.path.join(txt_store_path, each + ".txt")
            with open(txt_path, encoding=FILE_ENCODING) as txt:
                while True:
                    # Read one line from
                    line = txt.readline()
                    if not line:
                        break
                    line = line.rstrip('\r\n')
                    f.write(line)
                    f.write("\n")


class Pattern:
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


def detect_file_encoding(input_file):
    with open(input_file, 'rb') as f:
        text = f.read()
        res = chardet.detect(text)
        encoding = res['encoding']
    return encoding


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help='input file path')
    parser.add_argument('--output', type=str, help='output folder path')
    args = parser.parse_args()
    input_file = args.input
    output_path = args.output
    save_path = "./"

    # join_txt(
    #     txt_store_path=save_path,
    #     final_txt_path=save_path,
    # )
    # path = str(os.path.join(save_path, "output.txt"))
