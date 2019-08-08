#!/usr/bin/env python

import os
import subprocess
import click
from tqdm import tqdm


TMP_FOLDER = './TMP_FOLDER/'


def convert_pdf_img(pdf_file):
    if not(os.path.isdir(TMP_FOLDER)):
        os.mkdir(TMP_FOLDER)
    filename = os.path.basename(pdf_file)
    command = ['mutool', 'draw', '-o', 
               TMP_FOLDER+filename+'-%03d.png', 
               pdf_file]

    subprocess.run(command, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    # subprocess.run(command)
    files = os.listdir(TMP_FOLDER)
    return files


def page_is_colored(page_file_img):
    command = ['identify', '-colorspace', 'HSL', '-format',
               "%[fx:mean.g] %[fx:maxima.g]", page_file_img ]
    
    data = subprocess.run(command, capture_output=True, text=True)
    data = data.stdout.split()
    data = [float(value) for value in data]
    avg, peak = data[0], data[1]

    page_is_colored = False
    if peak == 1:
        page_is_colored = True
    elif peak > 0.65:
        if avg > 1.e-05:
            page_is_colored = True
        else:
            page_is_colored = False
    else:
        page_is_colored = False

    data = [avg, peak, page_is_colored]

    return page_is_colored


def get_pdf_info(pdf_file):
    images_files = convert_pdf_img(pdf_file)
    ncolor_pages = 0
    nbw_pages = 0

    for page in images_files:
        is_color = page_is_colored(TMP_FOLDER+page)
        # print(is_color)
        if is_color:
            ncolor_pages = ncolor_pages + 1
        else:
            nbw_pages = nbw_pages + 1

    for page in images_files:
        os.remove(TMP_FOLDER+page)

    page_info = {'total_pages' : ncolor_pages+nbw_pages,
                 'colored_pages': ncolor_pages,
                 'bw_pages' : nbw_pages}
    return page_info


#main script
@click.command()
@click.argument('pdf_file')
def main(pdf_file):
    if os.path.isfile(pdf_file):
        click.echo('Converting pdf to img...')
        image_files = convert_pdf_img(pdf_file)
        click.echo('Analyzing pdf page')
        image_files.sort()

        pages_info = []
        for page in tqdm(image_files):
            page_color = [page.strip('.png'), page_is_colored(TMP_FOLDER+page)]
            pages_info.append(page_color)
        for page in image_files:
            os.remove(TMP_FOLDER+page)
        os.removedirs(TMP_FOLDER)

        for page in pages_info:
            if page[1]:
                click.echo(page[0]+' is colored')
            else:
                click.echo(page[0]+' is not colored')

        return pages_info 
    else:
        click.echo("File didn't Exist")

if __name__ == '__main__':
    main()
