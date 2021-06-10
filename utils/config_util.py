"""Functions for reading configuration files."""
import os
from google.protobuf import text_format
from mint.protos import pipeline_pb2
import tensorflow.google as tf
from google3.third_party.tensorflow.python.lib.io import file_io  # pylint: disable=g-direct-tensorflow-import


def get_configs_from_pipeline_file(pipeline_config_path, config_override=None):
  """Reads configuration from a pipeline_pb2.TrainEvalPipelineConfig.

  Args:
    pipeline_config_path: Path to pipeline_pb2.TrainEvalPipelineConfig text
      proto.
    config_override: A pipeline_pb2.TrainEvalPipelineConfig text proto to
      override pipeline_config_path.

  Returns:
    Dictionary of configuration objects. Keys are `model`, `train_config`,
      `train_input_config`, `eval_input_config`. Values are the corresponding
      config objects.
  """
  pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
  with tf.gfile.GFile(pipeline_config_path, 'r') as f:
    proto_str = f.read()
    text_format.Merge(proto_str, pipeline_config)
  if config_override:
    text_format.Merge(config_override, pipeline_config)

  configs = {}
  configs['model'] = pipeline_config.multi_modal_model
  configs['train_config'] = pipeline_config.train_config
  configs['train_dataset'] = pipeline_config.train_dataset
  configs['eval_config'] = pipeline_config.eval_config
  configs['eval_dataset'] = pipeline_config.eval_dataset

  return configs


def create_pipeline_proto_from_configs(configs):
  """Creates a pipeline_pb2.TrainEvalPipelineConfig from configs dictionary.

  This function nearly performs the inverse operation of
  get_configs_from_pipeline_file(). Instead of returning a file path, it returns
  a `TrainEvalPipelineConfig` object.

  Args:
    configs: Dictionary of configs. See get_configs_from_pipeline_file().

  Returns:
    A fully populated pipeline_pb2.TrainEvalPipelineConfig.
  """
  pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
  pipeline_config.multi_modal_model.CopyFrom(configs['model'])
  pipeline_config.train_config.CopyFrom(configs['train_config'])
  pipeline_config.train_dataset.CopyFrom(configs['train_dataset'])
  pipeline_config.eval_config.CopyFrom(configs['eval_config'])
  pipeline_config.eval_dataset.CopyFrom(configs['eval_dataset'])
  return pipeline_config


def save_pipeline_config(pipeline_config, directory):
  """Saves a pipeline config text file to disk.

  Args:
    pipeline_config: A pipeline_pb2.TrainEvalPipelineConfig.
    directory: The model directory into which the pipeline config file will be
      saved.
  """
  if not file_io.file_exists(directory):
    file_io.recursive_create_dir(directory)
  pipeline_config_path = os.path.join(directory, 'pipeline.config')
  config_text = text_format.MessageToString(pipeline_config)
  with tf.gfile.Open(pipeline_config_path, 'wb') as f:
    tf.logging.info('Writing pipeline config file to %s', pipeline_config_path)
    f.write(config_text)