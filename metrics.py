import numpy as np
import os


def calculate_normal_metrics2(normals1, normals2):
    normals1_flat = normals1.reshape(-1, 3)
    normals2_flat = normals2.reshape(-1, 3)
    zero_indices_1 = np.where(~np.any(normals1_flat, axis=1))[0]
    valid_indices = np.setdiff1d(np.arange(len(normals1_flat)), zero_indices_1)
    valid_normals1 = normals1_flat[valid_indices]
    valid_normals2 = normals2_flat[valid_indices]
    
    dot_products = np.sum(valid_normals1 * valid_normals2, axis=1)
    dot_products = np.clip(dot_products, -1.0, 1.0)
    angles = np.arccos(dot_products)
    angle_degrees = np.degrees(angles)

    avg = np.mean(np.degrees(angles))
    median = np.median(np.degrees(angles))
    threshold_11_25 = (angle_degrees < 11.25).mean() * 100
    threshold_22_5 = (angle_degrees < 22.5).mean() * 100
    threshold_30 = (angle_degrees < 30).mean() * 100

    return avg, median, threshold_11_25, threshold_22_5, threshold_30


class Metric(object):
    def __init__(self):

        self.results = {}
        self.filters = []
        self.eval_keys = ['mean_angle', 'median_angle', 'threshold_11_25', 'threshold_22_5', 'threshold_30']

    def update_norm(self, gt, pred, filter_name):
        assert gt.shape == pred.shape

        results = calculate_normal_metrics2(gt, pred)

        if filter_name not in self.results:
            self.results[filter_name] = {}

        for key, value in zip(self.eval_keys, results):
            if key not in self.results[filter_name]:
                self.results[filter_name][key] = []
            self.results[filter_name][key].append(value)

        if filter_name not in self.filters:
            self.filters.append(filter_name)

    def save_results(self, output_directory):
        os.makedirs(output_directory, exist_ok=True)
        for filter_name in self.filters:
            output_file_path = os.path.join(output_directory, f"{filter_name}_evaluation.txt")
            with open(output_file_path, "w") as f:
                f.write("Evaluation Complete for Filter: {}\n".format(filter_name))
                for key in self.eval_keys:
                    avg_value = np.mean(self.results[filter_name][key])
                    f.write(f"{key}: {avg_value:.4f}\n")

            print(f"Evaluation results for {filter_name} saved to: {output_file_path}")
