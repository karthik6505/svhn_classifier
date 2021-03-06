"""
Copyright (c) 2017 Claudio Pomo

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

if __name__ == '__main__':
    import load
    from dp import Network

    train_samples, train_labels = load._train_samples, load._train_labels
    test_samples, test_labels = load._test_samples, load._test_labels

    print('Training set', train_samples.shape, train_labels.shape)
    print('    Test set', test_samples.shape, test_labels.shape)

    image_size = load.image_size
    num_labels = load.num_labels
    num_channels = load.num_channels


    def train_data_iterator(samples, labels, iteration_steps, chunkSize):
        if len(samples) != len(labels):
            raise Exception('Length of samples and labels must equal')
        stepStart = 0  # initial step
        i = 0
        while i < iteration_steps:
            stepStart = (i * chunkSize) % (labels.shape[0] - chunkSize)
            yield i, samples[stepStart:stepStart + chunkSize], labels[stepStart:stepStart + chunkSize]
            i += 1


    def test_data_iterator(samples, labels, chunkSize):
        if len(samples) != len(labels):
            raise Exception('Length of samples and labels must equal')
        stepStart = 0  # initial step
        i = 0
        while stepStart < len(samples):
            stepEnd = stepStart + chunkSize
            if stepEnd < len(samples):
                yield i, samples[stepStart:stepEnd], labels[stepStart:stepEnd]
                i += 1
            stepStart = stepEnd


    net = Network(
        train_batch_size=64, test_batch_size=500, pooling_scale=2,
        dropout_rate=0.9,
        base_learning_rate=0.001, decay_rate=0.99)
    net.define_inputs(
        train_samples_shape=(64, image_size, image_size, num_channels),
        train_labels_shape=(64, num_labels),
        test_samples_shape=(500, image_size, image_size, num_channels),
    )
    net.add_conv(patch_size=3, in_depth=num_channels, out_depth=32, activation='relu', pooling=False, name='conv1')
    net.add_conv(patch_size=3, in_depth=32, out_depth=32, activation='relu', pooling=True, name='conv2')
    net.add_conv(patch_size=3, in_depth=32, out_depth=32, activation='relu', pooling=False, name='conv3')
    net.add_conv(patch_size=3, in_depth=32, out_depth=32, activation='relu', pooling=True, name='conv4')

    net.add_fc(in_num_nodes=(image_size // 4) * (image_size // 4) * 32, out_num_nodes=128, activation='relu',
               name='fc1')
    net.add_fc(in_num_nodes=128, out_num_nodes=10, activation=None, name='fc2')

    net.define_model()
    net.run(train_samples, train_labels, test_samples, test_labels, train_data_iterator=train_data_iterator,
             iteration_steps=3000, test_data_iterator=test_data_iterator)
    #net.train(train_samples, train_labels, data_iterator=train_data_iterator, iteration_steps=3000)


else:
    raise Exception('main.py: Should Not Be Imported!!! Must Run by "python main.py"')
