from __future__ import print_function

from pylearn2.config import yaml_parse
from easy_1_preprocess import output_dir, n_features, pickle_x_train, pickle_x_test, pickle_y_train, pickle_y_test

import os

nn_save = os.path.join(output_dir, "nn_train.pkl")
nn_save_best = os.path.join(output_dir, "nn_train_best.pkl")

yaml = """\
!obj:pylearn2.train.Train {{
    dataset: &train !obj:pylearn2.datasets.dense_design_matrix.DenseDesignMatrix {{
        X: !pkl: '{x_train}',
        y: !pkl: '{y_train}',
        y_labels: 2,
    }},

    model: !obj:pylearn2.models.mlp.MLP {{
        layers : [
            !obj:pylearn2.models.mlp.RectifiedLinear {{
                layer_name: 'h0',
                dim: 500,
                sparse_init: 15,
                # Rather than using weight decay, we constrain the norms of the weight vectors
                max_col_norm: {max_norm}
            }},
            !obj:pylearn2.models.mlp.RectifiedLinear {{
                layer_name: 'h1',
                dim: 500,
                sparse_init: 15,
                # Rather than using weight decay, we constrain the norms of the weight vectors
                max_col_norm: {max_norm}
            }},
            !obj:pylearn2.models.mlp.Softmax {{
                layer_name: 'y',
                n_classes: 2,
                irange: 0,
                init_bias_target_marginals: *train
            }},
        ],
        nvis: {n_features},
    }},

    # We train using stochastic gradient descent
    algorithm: !obj:pylearn2.training_algorithms.sgd.SGD {{
        batch_size: 250,

        learning_rate: 1e-1,
        learning_rule: !obj:pylearn2.training_algorithms.learning_rule.Momentum {{
            init_momentum: 0.5,
        }},

        # We monitor how well we're doing during training on a validation set
        monitoring_dataset: {{
            'train' : *train,
            'valid' : !obj:pylearn2.datasets.dense_design_matrix.DenseDesignMatrix {{
                X: !pkl: '{x_test}',
                y: !pkl: '{y_test}',
                y_labels: 2,
            }},
        }},

        cost: !obj:pylearn2.costs.mlp.dropout.Dropout {{
            input_include_probs: {{
                'h0' : .8,
                'h1' : .8
            }},
            input_scales: {{
                'h0' : 1.,
                'h1' : 1.
            }}
        }},

        # We stop after 50 epochs
        termination_criterion: !obj:pylearn2.termination_criteria.EpochCounter {{
            max_epochs: 50,
        }},
    }},

    # We save the model whenever we improve on the validation set classification error
    extensions: [
        !obj:pylearn2.train_extensions.best_params.MonitorBasedSaveBest {{
             channel_name: 'valid_y_misclass',
             save_path: '{save_file_best}'
        }},
        # http://daemonmaker.blogspot.com/2014/12/monitoring-experiments-in-pylearn2.html
        !obj:pylearn2.train_extensions.live_monitoring.LiveMonitoring {{}},
        # Not sure what this does...
        #!obj:pylearn2.training_algorithms.sgd.LinearDecayOverEpoch {{
        #    start: 5,
        #    saturate: 100,
        #    decay_factor: .01
        #}}
    ],

    save_path: '{save_file}',
    save_freq: 1,
}}
""".format(
    n_features=n_features,
    max_norm=0.5,
    save_file=nn_save,
    save_file_best=nn_save_best,
    x_train=pickle_x_train,
    x_test=pickle_x_test,
    y_train=pickle_y_train,
    y_test=pickle_y_test
)


def main():
    ##########################################################################
    # Train NN
    ##########################################################################

    train = yaml_parse.load(yaml)
    train.main_loop()


if __name__ == "__main__":
    main()
