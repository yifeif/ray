// Copyright 2017 The Ray Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <algorithm>

#include "ray/stats/metric_exporter_client.h"

namespace ray {
namespace stats {

void StdoutExporterClient::ReportMetrics(const std::vector<MetricPoint> &points) {
  RAY_LOG(ERROR) << "Metric point size : " << points.size();
}

MetricExporterDecorator::MetricExporterDecorator(
    std::shared_ptr<MetricExporterClient> exporter)
    : exporter_(exporter) {}

void MetricExporterDecorator::ReportMetrics(const std::vector<MetricPoint> &points) {
  if (exporter_) {
    exporter_->ReportMetrics(points);
  }
}

// SANG-TODO Implement Metrics Agent Client.
  // // Initialize a rpc client to the new node manager.
  // std::unique_ptr<rpc::NodeManagerClient> client(
  //     new rpc::NodeManagerClient(node_info.node_manager_address(),
  //                                node_info.node_manager_port(), client_call_manager_));
  // remote_node_manager_clients_.emplace(node_id, std::move(client));
}  // namespace stats
}  // namespace ray
