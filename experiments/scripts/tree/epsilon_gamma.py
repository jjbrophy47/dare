"""
This experiment tests the accuracy of the decision trees.
BABC: Binary Attributes Binary Classification.
"""
import os
import sys
import time
import argparse

import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here + '/../../..')
sys.path.insert(0, here + '/../..')
from model import deterministic, detrace
from utility import data_util, exp_util, print_util


def vary_gamma(args, logger, out_dir, seed):

    # obtain data
    X_train, X_test, y_train, y_test = data_util.get_data(args.dataset, seed, data_dir=args.data_dir)

    # dataset statistics
    logger.info('train instances: {}'.format(X_train.shape[0]))
    logger.info('test instances: {}'.format(X_test.shape[0]))
    logger.info('attributes: {}'.format(X_train.shape[1]))

    logger.info('building d_tree...')
    start = time.time()
    d_tree = deterministic.Tree(max_depth=args.max_depth, verbose=args.verbose)
    d_tree = d_tree.fit(X_train, y_train)
    logger.info('{:.3f}s'.format(time.time() - start))

    exp_util.performance(d_tree, X_test, y_test, name='d_tree')

    aucs, accs = [], []
    gammas = np.linspace(0.01, 0.99)
    logger.info('gammas ({}): {}'.format(len(gammas), gammas))
    for i, gamma in enumerate(gammas):
        logger.info('[{}] epsilon: {:.2f}, gamma: {:.2f}...'.format(i, args.epsilon, gamma))
        start = time.time()
        dt_tree = detrace.Tree(epsilon=args.epsilon, gamma=gamma, max_depth=args.max_depth,
                               verbose=args.verbose, random_state=None)
        dt_tree = dt_tree.fit(X_train, y_train)

        proba = dt_tree.predict_proba(X_test)[:, 1]
        pred = dt_tree.predict(X_test)
        aucs.append(roc_auc_score(y_test, proba))
        accs.append(accuracy_score(y_test, pred))

        if args.verbose > 0:
            exp_util.performance(dt_tree, X_test, y_test, name='dt_tree', logger=logger)

    if args.save_results:
        np.save(os.path.join(out_dir, 'auc.npy'), aucs)
        np.save(os.path.join(out_dir, 'acc.npy'), accs)
        np.save(os.path.join(out_dir, 'gamma.npy'), gammas)


def main(args):

    # run experiment multiple times
    for i in range(args.repeats):

        # create output dir
        ep_dir = os.path.join(args.out_dir, args.dataset, 'rs{}'.format(args.rs), 'ep{}'.format(args.epsilon))
        os.makedirs(ep_dir, exist_ok=True)

        # create logger
        logger = print_util.get_logger(os.path.join(ep_dir, 'log.txt'))
        logger.info(args)
        logger.info('\nRun {}, seed: {}'.format(i + 1, args.rs))

        # run experiment
        vary_gamma(args, logger, ep_dir, seed=args.rs)
        args.rs += 1

        # remove logger
        print_util.remove_logger(logger)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, default='output/tree/epsilon_gamma', help='output directory.')
    parser.add_argument('--data_dir', type=str, default='data', help='data directory.')
    parser.add_argument('--dataset', default='synthetic', help='dataset to use for the experiment.')
    parser.add_argument('--rs', type=int, default=1, help='random state.')
    parser.add_argument('--repeats', type=int, default=1, help='number of times to perform the experiment.')
    parser.add_argument('--save_results', action='store_true', default=False, help='save results.')
    parser.add_argument('--epsilon', type=float, default=0.1, help='efficiency parameter for tree.')
    parser.add_argument('--max_depth', type=int, default=4, help='maximum depth of the tree.')
    parser.add_argument('--verbose', type=int, default=0, help='verbosity level.')
    args = parser.parse_args()
    main(args)