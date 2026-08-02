import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import rclpy
from rclpy.node import Node


def escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


class RobotekRosExporter(Node):
    def __init__(self) -> None:
        super().__init__("robotek_ros_exporter")

        self._metrics_lock = threading.Lock()
        self._metrics = ""
        self._collection_errors = 0

        self.refresh_metrics()

        self.create_timer(
            5.0,
            self.refresh_metrics,
        )

    def refresh_metrics(self) -> None:
        try:
            nodes = sorted(set(self.get_node_names_and_namespaces()))

            topics = sorted(topic for topic, _types in self.get_topic_names_and_types())

            lines: list[str] = [
                "# HELP robotek_ros_exporter_up Whether the ROS exporter is operational.",
                "# TYPE robotek_ros_exporter_up gauge",
                "robotek_ros_exporter_up 1",
                "",
                "# HELP robotek_ros_nodes Number of discovered ROS 2 nodes.",
                "# TYPE robotek_ros_nodes gauge",
                f"robotek_ros_nodes {len(nodes)}",
                "",
                "# HELP robotek_ros_topics Number of discovered ROS 2 topics.",
                "# TYPE robotek_ros_topics gauge",
                f"robotek_ros_topics {len(topics)}",
                "",
                "# HELP robotek_ros_node_up Whether a ROS 2 node is visible.",
                "# TYPE robotek_ros_node_up gauge",
            ]

            for node_name, namespace in nodes:
                if namespace == "/":
                    full_name = f"/{node_name}"
                else:
                    full_name = f"{namespace.rstrip('/')}/{node_name}"

                lines.append(f'robotek_ros_node_up{{node="{escape_label(full_name)}"}} 1')

            lines.extend(
                [
                    "",
                    "# HELP robotek_ros_topic_publishers Number of publishers for a ROS 2 topic.",
                    "# TYPE robotek_ros_topic_publishers gauge",
                ]
            )

            for topic in topics:
                publishers = self.count_publishers(topic)

                lines.append(
                    f'robotek_ros_topic_publishers{{topic="{escape_label(topic)}"}} {publishers}'
                )

            lines.extend(
                [
                    "",
                    "# HELP robotek_ros_topic_subscribers Number of subscribers for a ROS 2 topic.",
                    "# TYPE robotek_ros_topic_subscribers gauge",
                ]
            )

            for topic in topics:
                subscribers = self.count_subscribers(topic)

                lines.append(
                    f'robotek_ros_topic_subscribers{{topic="{escape_label(topic)}"}} {subscribers}'
                )

            lines.extend(
                [
                    "",
                    "# HELP robotek_ros_collection_errors_total Total ROS graph collection errors.",
                    "# TYPE robotek_ros_collection_errors_total counter",
                    (f"robotek_ros_collection_errors_total {self._collection_errors}"),
                    "",
                ]
            )

            rendered = "\n".join(lines)

        except Exception as error:
            self._collection_errors += 1

            self.get_logger().error(f"ROS graph collection failed: {error}")

            rendered = "\n".join(
                [
                    "# HELP robotek_ros_exporter_up Whether the ROS exporter is operational.",
                    "# TYPE robotek_ros_exporter_up gauge",
                    "robotek_ros_exporter_up 0",
                    "",
                    "# HELP robotek_ros_collection_errors_total Total ROS graph collection errors.",
                    "# TYPE robotek_ros_collection_errors_total counter",
                    (f"robotek_ros_collection_errors_total {self._collection_errors}"),
                    "",
                ]
            )

        with self._metrics_lock:
            self._metrics = rendered

    def render_metrics(self) -> bytes:
        with self._metrics_lock:
            return self._metrics.encode("utf-8")


class MetricsHandler(BaseHTTPRequestHandler):
    exporter: RobotekRosExporter

    def do_GET(self) -> None:
        if self.path == "/metrics":
            payload = self.exporter.render_metrics()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain; version=0.0.4; charset=utf-8",
            )
            self.send_header(
                "Content-Length",
                str(len(payload)),
            )
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path in ("/-/ready", "/healthz"):
            payload = b"OK\n"

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8",
            )
            self.send_header(
                "Content-Length",
                str(len(payload)),
            )
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(
        self,
        _format: str,
        *_args: object,
    ) -> None:
        return


def main(args=None) -> None:
    rclpy.init(args=args)

    exporter = RobotekRosExporter()

    MetricsHandler.exporter = exporter

    port = int(
        os.environ.get(
            "ROBOTEK_METRICS_PORT",
            "9108",
        )
    )

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        MetricsHandler,
    )

    server_thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    server_thread.start()

    exporter.get_logger().info(f"Robotek ROS metrics listening on port {port}")

    try:
        rclpy.spin(exporter)
    finally:
        server.shutdown()
        server.server_close()
        exporter.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
