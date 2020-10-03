import importlib
import logging
import json
import os
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)

# For caching provider instantiations across API calls of one python session
_provider_instances = {}


def _import_aws(provider_config):
    from ray.autoscaler._private.aws.node_provider import AWSNodeProvider
    return AWSNodeProvider


def _import_gcp(provider_config):
    from ray.autoscaler._private.gcp.node_provider import GCPNodeProvider
    return GCPNodeProvider


def _import_azure(provider_config):
    from ray.autoscaler._private.azure.node_provider import AzureNodeProvider
    return AzureNodeProvider


def _import_local(provider_config):
    if "coordinator_address" in provider_config:
        from ray.autoscaler._private.local.coordinator_node_provider import (
            CoordinatorSenderNodeProvider)
        return CoordinatorSenderNodeProvider
    else:
        from ray.autoscaler._private.local.node_provider import \
            LocalNodeProvider
        return LocalNodeProvider


def _import_kubernetes(provider_config):
    from ray.autoscaler._private.kubernetes.node_provider import \
        KubernetesNodeProvider
    return KubernetesNodeProvider


def _import_staroid(provider_config):
    from ray.autoscaler._private.staroid.node_provider import \
        StaroidNodeProvider
    return StaroidNodeProvider


def _load_local_example_config():
    import ray.autoscaler.local as ray_local
    return os.path.join(
        os.path.dirname(ray_local.__file__), "example-full.yaml")


def _load_kubernetes_example_config():
    import ray.autoscaler.kubernetes as ray_kubernetes
    return os.path.join(
        os.path.dirname(ray_kubernetes.__file__), "example-full.yaml")


def _load_aws_example_config():
    import ray.autoscaler.aws as ray_aws
    return os.path.join(os.path.dirname(ray_aws.__file__), "example-full.yaml")


def _load_gcp_example_config():
    import ray.autoscaler.gcp as ray_gcp
    return os.path.join(os.path.dirname(ray_gcp.__file__), "example-full.yaml")


def _load_azure_example_config():
    import ray.autoscaler.azure as ray_azure
    return os.path.join(
        os.path.dirname(ray_azure.__file__), "example-full.yaml")


def _load_staroid_example_config():
    import ray.autoscaler.staroid as ray_staroid
    return os.path.join(
        os.path.dirname(ray_staroid.__file__), "example-full.yaml")


def _import_external(provider_config):
    provider_cls = _load_class(path=provider_config["module"])
    return provider_cls


_NODE_PROVIDERS = {
    "local": _import_local,
    "aws": _import_aws,
    "gcp": _import_gcp,
    "azure": _import_azure,
    "staroid": _import_staroid,
    "kubernetes": _import_kubernetes,
    "external": _import_external  # Import an external module
}

_PROVIDER_PRETTY_NAMES = {
    "local": "Local",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "staroid": "Staroid",
    "kubernetes": "Kubernetes",
    "external": "External"
}

_DEFAULT_CONFIGS = {
    "local": _load_local_example_config,
    "aws": _load_aws_example_config,
    "gcp": _load_gcp_example_config,
    "azure": _load_azure_example_config,
    "staroid": _load_staroid_example_config,
    "kubernetes": _load_kubernetes_example_config,
}


def _load_class(path):
    """Load a class at runtime given a full path.

    Example of the path: mypkg.mysubpkg.myclass
    """
    class_data = path.split(".")
    if len(class_data) < 2:
        raise ValueError(
            "You need to pass a valid path like mymodule.provider_class")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]
    module = importlib.import_module(module_path)
    return getattr(module, class_str)


def _get_node_provider(provider_config: Dict[str, Any],
                       cluster_name: str,
                       use_cache: bool = True) -> Any:
    importer = _NODE_PROVIDERS.get(provider_config["type"])
    if importer is None:
        raise NotImplementedError("Unsupported node provider: {}".format(
            provider_config["type"]))
    provider_cls = importer(provider_config)
    provider_key = (json.dumps(provider_config, sort_keys=True), cluster_name)
    if use_cache and provider_key in _provider_instances:
        return _provider_instances[provider_key]

    new_provider = provider_cls(provider_config, cluster_name)

    if use_cache:
        _provider_instances[provider_key] = new_provider

    return new_provider


def _clear_provider_cache():
    global _provider_instances
    _provider_instances = {}


def _get_default_config(provider_config):
    """Retrieve a node provider.

    This is an INTERNAL API. It is not allowed to call this from any Ray
    package outside the autoscaler.
    """
    if provider_config["type"] == "external":
        return {}
    load_config = _DEFAULT_CONFIGS.get(provider_config["type"])
    if load_config is None:
        raise NotImplementedError("Unsupported node provider: {}".format(
            provider_config["type"]))
    path_to_default = load_config()
    with open(path_to_default) as f:
        defaults = yaml.safe_load(f)

    return defaults
