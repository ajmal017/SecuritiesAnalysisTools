import os
from pptx import Presentation

from libs.outputs.pptx_resources import title_presentation
from libs.outputs.pptx_resources import intro_slide
from libs.outputs.pptx_resources import make_BCI_slides, make_MCI_slides
from libs.outputs.pptx_resources import make_CCI_slides, make_TCI_slides
from libs.outputs.pptx_resources import make_fund_slides
from libs.utils import TEXT_COLOR_MAP

PPTX_NAME_COLOR = TEXT_COLOR_MAP["purple"]
NORMAL_COLOR = TEXT_COLOR_MAP["white"]


def slide_creator(analysis: dict, config: dict = None, year=None, version=None):
    """ High-level function for converting inventors spreadsheet to slides """

    print("")
    print("Starting presentation creation.")
    if config is not None:
        year = config['date_release'].split('-')[0]
        version = config['version']
    elif year is None:
        print(
            f"ERROR: 'year', 'config', [and 'version'] {year} provided in 'slide_creator'.")
        return
    else:
        year = year
        version = version

    prs = Presentation()

    prs = title_presentation(prs, year, VERSION=version)
    prs = intro_slide(prs)
    prs = make_MCI_slides(prs, analysis.get('_METRICS_', {}))
    prs = make_CCI_slides(prs)
    prs = make_BCI_slides(prs)
    prs = make_TCI_slides(prs)
    prs = make_fund_slides(prs, analysis)

    out_dir = "output/"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    title = f"Financial Analysis {year}.pptx"
    prs.save(f"{out_dir}{title}")

    print(f"Presentation '{PPTX_NAME_COLOR}{title}{NORMAL_COLOR}' created.")
