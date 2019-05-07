# -*- coding: utf-8 -*-
"""A vanilla CNN architecture for CIFAR-10."""

import torch
from torch import nn
from .testproblems_modules import net_cifar10_3c3d
from ..datasets.cifar10 import cifar10
from .testproblem import TestProblem

class cifar10_3c3d(TestProblem):
    def __init__(self, batch_size, weight_decay=0.002):
        super(cifar10_3c3d, self).__init__(batch_size, weight_decay)

    def set_up(self):
        """Set up the vanilla CNN test problem on Cifar-10."""
        self.data = cifar10(self._batch_size)
        self.loss_function = nn.CrossEntropyLoss()
        self.net = net_cifar10_3c3d(num_outputs=10)
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net.to(self._device)

    def get_regularization_loss(self):
        # iterate through all layers
        layer_norms = []
        for parameters_name, parameters in self.net.named_parameters():
            # penalize only the non bias layer parameters
            if 'bias' not in parameters_name:
                # L2 regularization
                layer_norms.append(parameters.pow(2).sum())

        regularization_loss = 0.5 * sum(layer_norms)

        return self._weight_decay * regularization_loss

    def get_batch_loss_and_accuracy(self):
        inputs, labels = self._get_next_batch()
        inputs = inputs.to(self._device)
        labels = labels.to(self._device)
        correct = 0.0
        total = 0.0

        # in evaluation phase is no gradient needed
        if self.phase in ["train_eval", "test"]:
            with torch.no_grad():
                outputs = self.net(inputs)
                loss = self.loss_function(outputs, labels)
        else:
            outputs = self.net(inputs)
            loss = self.loss_function(outputs, labels)

        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        accuracy = correct/total
        return loss, accuracy