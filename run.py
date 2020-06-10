import argparse
import logging

import yaml
import pandas as pd

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.INFO)
logger = logging.getLogger('run-pipeline')

from src.s3_upload import upload_to_s3
from src.s3_download import download_from_s3
from src.clean import clean_base
from src.featurize import featurize
from src.model import model
from src.offline_score import scoring
from src.create_score_db import create_score_db

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Acquire, clean, and create features from cloud data")

    parser.add_argument('step', help='Which step to run', choices=['upload', 'download', 'clean', 'featurize',
                                                                   'eda', 'model', 'score', 'create_db'])
    parser.add_argument('--input', '-i', default=None, help='Path to input data')
    parser.add_argument('--input_profile', '-i_p', default=None, help='Path to profile data')
    parser.add_argument('--lfp', default=None, help='Local file path to store artifacts')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--output', '-o', default=None, help='Path to save output CSV (optional, default = None)')
    parser.add_argument('--truncate', '-t', default=False, action="store_true",
                        help="If given, delete current records from prediction table before create_all")

    args = parser.parse_args()

    # Load configuration file for parameters and tmo path
    with open(args.config, "r") as f:
        try:
            config = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            logger.error('Config file %s not found', args.config)
            raise SystemExit("Provide valid path!")

    logger.info("Configuration file loaded from %s" % args.config)

    if args.input is not None and args.step != 'upload':
        try:
            input = pd.read_csv(args.input)
            logger.info('Input data loaded from %s', args.input)
        except FileNotFoundError as e:
            logger.error('Input file %s not found', args.input)
            raise SystemExit("Provide valid path!")

    if args.input_profile is not None:
        try:
            input_profile = pd.read_csv(args.input_profile)
            logger.info('Input profile data loaded from %s', args.input)
        except FileNotFoundError as e:
            logger.error('Input profile file %s not found', args.input)
            raise SystemExit("Provide valid path!")

    if args.step == 'upload':
        upload_to_s3(args.input, **config['s3_upload'])
    if args.step == 'download':
        download_from_s3(args.lfp, **config['s3_download'])
    elif args.step == 'clean':
        output = clean_base(input, **config['clean'])
    elif args.step == 'featurize':
        output = featurize(input, input_profile, args.lfp, **config['featurize'])
    elif args.step == 'model':
        model(input, args.lfp, **config['model'])
    elif args.step == 'score':
        output = scoring(args.lfp, **config['score'])
    elif args.step == 'create_db':
        if args.truncate:
            create_score_db(input, 1, **config['database'])
        else:
            create_score_db(input, 0, **config['database'])

    if args.output is not None and output is not None:
        output.to_csv(args.output, index=False)
        logger.info("Output saved to %s" % args.output)
