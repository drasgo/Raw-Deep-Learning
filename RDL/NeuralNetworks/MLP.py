from RDL.NeuralNetworks.baseNeuralNetwork import BaseNeuralNetwork
from RDL.configs.debug import Verbosity, logger
import numpy


class MLP(BaseNeuralNetwork):
    def __init__(self, verbose: Verbosity=Verbosity.RELEASE):
        super().__init__(verbose)

    def forward(self, input_data):
        import pprint

        input_data = self.prepare_data(input_data)
        # Add check for input data. E.g. correct size, all numeric values, etc.
        output = None
        for input_layer in self.input_layers:
            # TODO: implement multiple input layers
            prev_layer = input_layer
            prev_layer["data"] = input_data

            while True:
                curr_layer = self.structure[prev_layer["output_layer"]]
                output_data = (
                    numpy.dot(curr_layer["weight"], prev_layer["data"])
                    + curr_layer["bias"]
                )
                output_data = curr_layer["activation"].forward(output_data)
                curr_layer["data"] = output_data
                prev_layer = curr_layer

                print("\n\n\n")
                print("layer " + curr_layer["name"] + ". result: ")
                pprint.pprint(output_data)

                if curr_layer["type"] == "output":
                    output = curr_layer["data"]
                    break

        return output

    def backward(self, output_data, target_data):
        """
        Compute sensitivities from m to 1 layer
        Then new_W(i) = old_W(i) - decay * S(i) (sensitivity of layer i) * (input to layer i)T (meaning transpose of input layer i)
        sensitivity of i ( S(i) ) = derivative of function Fi * old_W(i+1)T * S(i+1)
        except for layer m, where sensitivity of m ( S(m) ) = derivative of function Fi (usually linear) * derivative of loss (integer)
        """
        loss = self.loss_function.forward(output_data, target_data)
        loss_derivative = self.loss_function.derivative(output_data, target_data)

        for output_layer in self.output_layers:
            curr_layer = self.structure[output_layer]

            while True:
                if curr_layer["type"] == "input":
                    break

                elif curr_layer["type"] == "output":
                    # S(output) = f'(x) * loss'
                    sensitivity = (
                        curr_layer["activation"].derivative(curr_layer["data"])
                        * loss_derivative
                    )

                else:
                    # S(i) = f'(x) * W(i+1)T * S(i+1)
                    prev_layer = self.structure[curr_layer["output_layer"]]
                    sensitivity = (
                        curr_layer["activation"].derivative(curr_layer["data"])
                        * numpy.transpose(prev_layer["weight"])
                        * prev_layer["sensitivity"]
                    )

                curr_layer["sensitivity"] = sensitivity
                updates = sensitivity * numpy.transpose(
                    self.structure[curr_layer["input_layer"]]["data"]
                )
                curr_layer["weight_update"] += updates
        return loss
