import tensorflow as tf
import numpy as np
from .common import _FLOATX, _EPSILON

import tensorflow.compat.v1 as tfv1
tfv1.disable_v2_behavior()

# INTERNAL UTILS

_SESSION = None


def _get_session():
    global _SESSION
    if _SESSION is None:
        _SESSION = tfv1.Session('')
    return _SESSION


def _set_session(session):
    global _SESSION
    _SESSION = session


# VARIABLE MANIPULATION

def variable(value, dtype=_FLOATX, name=None):
    v = tfv1.Variable(np.asarray(value, dtype=dtype), name=name)
    _get_session().run(v.initializer)
    return v


def placeholder(shape=None, ndim=None, dtype=_FLOATX, name=None):
    if not shape:
        if ndim:
            shape = [None for _ in range(ndim)]
    return tfv1.placeholder(dtype, shape=shape, name=name)


def shape(x):
    return x.get_shape()


def ndim(x):
    return len(x.get_shape())


def eval(x):
    '''Run a graph.
    '''
    return x.eval(session=_get_session())


def zeros(shape, dtype=_FLOATX, name=None):
    return variable(np.zeros(shape), dtype, name)


def ones(shape, dtype=_FLOATX, name=None):
    return variable(np.ones(shape), dtype, name)


def ones_like(x, name=None):
    return tfv1.ones_like(x)


def zeros_like(x, name=None):
    return tfv1.zeros_like(x)


def count_params(x):
    '''Return number of scalars in a tensor.
    '''
    shape = x.get_shape()
    return np.prod([shape[i]._value for i in range(len(shape))])


def cast(x, dtype):
    return tfv1.cast(x, dtype)


# LINEAR ALGEBRA

def dot(x, y):
    return tfv1.matmul(x, y)


def transpose(x):
    return tfv1.transpose(x)


def gather(reference, indices):
    '''reference: a tensor.
    indices: an int tensor of indices.

    Return: a tensor of same type as reference.
    '''
    return tfv1.gather(reference, indices)


# ELEMENT-WISE OPERATIONS

def max(x, axis=None, keepdims=False):
    if axis is not None and axis < 0:
        axis = axis % len(x.get_shape())
    return tfv1.reduce_max(x, reduction_indices=axis, keep_dims=keepdims)


def min(x, axis=None, keepdims=False):
    if axis is not None and axis < 0:
        axis = axis % len(x.get_shape())
    return tfv1.reduce_min(x, reduction_indices=axis, keep_dims=keepdims)


def sum(x, axis=None, keepdims=False):
    '''Sum of the values in a tensor, alongside the specified axis.
    '''
    if axis is not None and axis < 0:
        axis = axis % len(x.get_shape())
    return tfv1.reduce_sum(x, reduction_indices=axis, keep_dims=keepdims)


def prod(x, axis=None, keepdims=False):
    '''Multiply the values in a tensor, alongside the specified axis.
    '''
    return tfv1.reduce_prod(x, reduction_indices=axis, keep_dims=keepdims)


def std(x, axis=None, keepdims=False):
    if axis is not None and axis < 0:
        axis = axis % len(x.get_shape())
    if x.dtype.base_dtype == tfv1.bool:
        x = tfv1.cast(x, _FLOATX)
    m = tfv1.reduce_mean(x, reduction_indices=axis, keep_dims=keepdims)
    devs_squared = tfv1.square(x - m)
    return tfv1.sqrt(tfv1.reduce_mean(devs_squared,
                                  reduction_indices=axis,
                                  keep_dims=keepdims))


def mean(x, axis=None, keepdims=False):
    if axis is not None and axis < 0:
        axis = axis % len(x.get_shape())
    if x.dtype.base_dtype == tfv1.bool:
        x = tfv1.cast(x, _FLOATX)
    return tfv1.reduce_mean(x, reduction_indices=axis, keep_dims=keepdims)


def any(x, axis=None, keepdims=False):
    '''Bitwise reduction (logical OR).

    Return array of int8 (0s and 1s).
    '''
    if axis is not None and axis < 0:
        axis = axis % len(x.get_shape())
    x = tfv1.cast(x, tfv1.bool)
    x = tfv1.reduce_any(x, reduction_indices=axis, keep_dims=keepdims)
    return tfv1.cast(x, tfv1.int8)


def argmax(x, axis=-1):
    if axis < 0:
        axis = axis % len(x.get_shape())
    return tfv1.argmax(x, axis)


def argmin(x, axis=-1):
    if axis < 0:
        axis = axis % len(x.get_shape())
    return tfv1.argmin(x, axis)


def square(x):
    return tfv1.square(x)


def abs(x):
    return tfv1.abs(x)


def sqrt(x):
    x = tfv1.clip_by_value(x, tfv1.cast(0., dtype=_FLOATX),
                         tfv1.cast(np.inf, dtype=_FLOATX))
    return tfv1.sqrt(x)


def exp(x):
    return tfv1.exp(x)


def log(x):
    return tfv1.log(x)


def round(x):
    return tfv1.round(x)


def pow(x, a):
    return tfv1.pow(x, a)


def clip(x, min_value, max_value):
    if max_value < min_value:
        max_value = min_value
    return tfv1.clip_by_value(x, tfv1.cast(min_value, dtype=_FLOATX),
                            tfv1.cast(max_value, dtype=_FLOATX))


def equal(x, y):
    return tfv1.equal(x, y)


def maximum(x, y):
    return tfv1.maximum(x, y)


def minimum(x, y):
    return tfv1.minimum(x, y)


# SHAPE OPERATIONS

def concatenate(tensors, axis=-1):
    if axis < 0:
        axis = axis % len(tensors[0].get_shape())
    return tfv1.concat(axis, tensors)


def reshape(x, shape):
    return tfv1.reshape(x, shape)


def permute_dimensions(x, pattern):
    '''Transpose dimensions.

    pattern should be a tuple or list of
    dimension indices, e.g. [0, 2, 1].
    '''
    return tfv1.transpose(x, perm=pattern)


def resize_images(X, height_factor, width_factor, dim_ordering):
    '''Resize the images contained in a 4D tensor of shape
    - [batch, channels, height, width] (for 'th' dim_ordering)
    - [batch, height, width, channels] (for 'tf' dim_ordering)
    by a factor of (height_factor, width_factor). Both factors should be
    positive integers.
    '''
    if dim_ordering == 'th':
        new_height = shape(X)[2].value * height_factor
        new_width = shape(X)[3].value * width_factor
        X = permute_dimensions(X, [0, 2, 3, 1])
        X = tfv1.image.resize_nearest_neighbor(X, (new_height, new_width))
        return permute_dimensions(X, [0, 3, 1, 2])
    elif dim_ordering == 'tf':
        new_height = shape(X)[1].value * height_factor
        new_width = shape(X)[2].value * width_factor
        return tfv1.image.resize_nearest_neighbor(X, (new_height, new_width))
    else:
        raise Exception('Invalid dim_ordering: ' + dim_ordering)


def repeat_elements(x, rep, axis):
    '''Repeats the elements of a tensor along an axis, like np.repeat

    If x has shape (s1, s2, s3) and axis=1, the output
    will have shape (s1, s2 * rep, s3)
    '''
    x_shape = x.get_shape().as_list()
    # slices along the repeat axis
    splits = tfv1.split(axis, x_shape[axis], x)
    # repeat each slice the given number of reps
    x_rep = [s for s in splits for i in range(rep)]
    return tfv1.concat(axis, x_rep)


def repeat(x, n):
    '''Repeat a 2D tensor:

    if x has shape (samples, dim) and n=2,
    the output will have shape (samples, 2, dim)
    '''
    tensors = [x] * n
    stacked = tfv1.pack(tensors)
    return tfv1.transpose(stacked, (1, 0, 2))


def tile(x, n):
    return tfv1.tile(x, n)


def flatten(x):
    return tfv1.reshape(x, [-1])


def batch_flatten(x):
    '''Turn a n-D tensor into a 2D tensor where
    the first dimension is conserved.
    '''
    x = tfv1.reshape(x, [-1, np.prod(x.get_shape()[1:].as_list())])
    return x


def expand_dims(x, dim=-1):
    '''Add a 1-sized dimension at index "dim".
    '''
    return tfv1.expand_dims(x, dim)


def squeeze(x, axis):
    '''Remove a 1-dimension from the tensor at index "axis".
    '''
    return tfv1.squeeze(x, [axis])


def temporal_padding(x, padding=1):
    '''Pad the middle dimension of a 3D tensor
    with "padding" zeros left and right.
    '''
    pattern = [[0, 0], [padding, padding], [0, 0]]
    return tfv1.pad(x, pattern)


def spatial_2d_padding(x, padding=(1, 1), dim_ordering='th'):
    '''Pad the 2nd and 3rd dimensions of a 4D tensor
    with "padding[0]" and "padding[1]" (resp.) zeros left and right.
    '''
    if dim_ordering == 'th':
        pattern = [[0, 0], [0, 0],
                   [padding[0], padding[0]], [padding[1], padding[1]]]
    else:
        pattern = [[0, 0],
                   [padding[0], padding[0]], [padding[1], padding[1]],
                   [0, 0]]
    return tfv1.pad(x, pattern)


# VALUE MANIPULATION

def get_value(x):
    '''Technically the same as eval() for TF.
    '''
    return x.eval(session=_get_session())


def set_value(x, value):
    tfv1.assign(x, np.asarray(value)).op.run(session=_get_session())


# GRAPH MANIPULATION

class Function(object):

    def __init__(self, inputs, outputs, updates=[]):
        assert type(inputs) in {list, tuple}
        assert type(outputs) in {list, tuple}
        assert type(updates) in {list, tuple}
        self.inputs = list(inputs)
        self.outputs = list(outputs)
        with tfv1.control_dependencies(self.outputs):
            self.updates = [tfv1.assign(p, new_p) for (p, new_p) in updates]

    def __call__(self, inputs):
        assert type(inputs) in {list, tuple}
        names = [v.name for v in self.inputs]
        feed_dict = dict(zip(names, inputs))
        session = _get_session()
        updated = session.run(self.outputs + self.updates, feed_dict=feed_dict)
        return updated[:len(self.outputs)]


def function(inputs, outputs, updates=[]):
    return Function(inputs, outputs, updates=updates)


def gradients(loss, variables):
    return tfv1.gradients(loss, variables)


# CONTROL FLOW

def rnn(step_function, inputs, initial_states,
        go_backwards=False, masking=True):
    '''Iterates over the time dimension of a tensor.

    Parameters
    ----------
    inputs: tensor of temporal data of shape (samples, time, ...)
        (at least 3D).
    step_function:
        Parameters:
            input: tensor with shape (samples, ...) (no time dimension),
                representing input for the batch of samples at a certain
                time step.
            states: list of tensors.
        Returns:
            output: tensor with shape (samples, ...) (no time dimension),
            new_states: list of tensors, same length and shapes
                as 'states'.
    initial_states: tensor with shape (samples, ...) (no time dimension),
        containing the initial values for the states used in
        the step function.
    go_backwards: boolean. If True, do the iteration over
        the time dimension in reverse order.
    masking: boolean. If true, any input timestep inputs[s, i]
        that is all-zeros will be skipped (states will be passed to
        the next step unchanged) and the corresponding output will
        be all zeros.

    Returns
    -------
    A tuple (last_output, outputs, new_states).
        last_output: the latest output of the rnn, of shape (samples, ...)
        outputs: tensor with shape (samples, time, ...) where each
            entry outputs[s, t] is the output of the step function
            at time t for sample s.
        new_states: list of tensors, latest states returned by
            the step function, of shape (samples, ...).
    '''
    inputs = tfv1.transpose(inputs, (1, 0, 2))
    input_list = tfv1.unpack(inputs)

    states = initial_states
    successive_states = []
    successive_outputs = []
    if go_backwards:
        input_list.reverse()
    for input in input_list:
        output, new_states = step_function(input, states)
        if masking:
            # for now we raise an exception because tfv1.reduce_any will not work
            raise Exception("Masking is Theano-only for the time being.")

            # if all-zero input timestep, return
            # all-zero output and unchanged states
            switch = tfv1.reduce_any(input)
            output = tfv1.python.control_flow_ops.cond(switch,
                                                     lambda: output,
                                                     lambda: 0. * output)
            return_states = []
            for state, new_state in zip(states, new_states):
                return_states.append(tfv1.python.control_flow_ops.cond(switch,
                                                                     lambda: new_state,
                                                                     lambda: state))
            states = return_states
        else:
            states = new_states
        successive_outputs.append(output)
        successive_states.append(states)

    last_output = successive_outputs[-1]
    outputs = tfv1.pack(successive_outputs)
    new_states = successive_states[-1]

    outputs = tfv1.transpose(outputs, (1, 0, 2))
    return last_output, outputs, new_states


def switch(condition, then_expression, else_expression):
    '''condition: scalar tensor.
    '''
    return tfv1.python.control_flow_ops.cond(condition,
                                           lambda: then_expression,
                                           lambda: else_expression)


# NN OPERATIONS

def relu(x, alpha=0., max_value=None):
    '''ReLU.

    alpha: slope of negative section.
    '''
    negative_part = tfv1.nn.relu(-x)
    x = tfv1.nn.relu(x)
    if max_value is not None:
        x = tfv1.clip_by_value(x, tfv1.cast(0., dtype=_FLOATX),
                             tfv1.cast(max_value, dtype=_FLOATX))
    x -= tfv1.constant(alpha, dtype=_FLOATX) * negative_part
    return x


def softmax(x):
    return tfv1.nn.softmax(x)


def softplus(x):
    return tfv1.nn.softplus(x)


def categorical_crossentropy(output, target, from_logits=False):
    '''Note: tfv1.nn.softmax_cross_entropy_with_logits
    expects logits, Keras expects probabilities.
    '''
    if not from_logits:
        # scale preds so that the class probas of each sample sum to 1
        output /= tfv1.reduce_sum(output,
                                reduction_indices=len(output.get_shape())-1,
                                keep_dims=True)
        # manual computation of crossentropy
        output = tfv1.clip_by_value(output, tfv1.cast(_EPSILON, dtype=_FLOATX),
                                  tfv1.cast(1.-_EPSILON, dtype=_FLOATX))
        return - tfv1.reduce_sum(target * tfv1.log(output),
                               reduction_indices=len(output.get_shape())-1)
    else:
        return tfv1.nn.softmax_cross_entropy_with_logits(output, target)


def binary_crossentropy(output, target, from_logits=False):
    '''Note: tfv1.nn.sigmoid_cross_entropy_with_logits
    expects logits, Keras expects probabilities.
    '''
    if not from_logits:
        # transform back to logits
        output = tfv1.clip_by_value(output, tfv1.cast(_EPSILON, dtype=_FLOATX),
                                  tfv1.cast(1.-_EPSILON, dtype=_FLOATX))
        output = tfv1.log(output / (1 - output))
    return tfv1.nn.sigmoid_cross_entropy_with_logits(output, target)


def sigmoid(x):
    return tfv1.nn.sigmoid(x)


def hard_sigmoid(x):
    x = (0.2 * x) + 0.5
    x = tfv1.clip_by_value(x, tfv1.cast(0., dtype=_FLOATX),
                         tfv1.cast(1., dtype=_FLOATX))
    return x


def tanh(x):
    return tfv1.nn.tanh(x)


def dropout(x, level, seed=None):
    retain_prob = 1. - level
    if seed is None:
        seed = np.random.randint(10e6)
    # the dummy 1. works around a TF bug
    # (float32_ref vs. float32 incomptability)
    return tfv1.nn.dropout(x * 1., retain_prob, seed=seed)


def l2_normalize(x, axis):
    if axis < 0:
        axis = axis % len(x.get_shape())
    return tfv1.nn.l2_normalize(x, dim=axis)


# CONVOLUTIONS


def conv2d(x, kernel, strides=(1, 1), border_mode='valid', dim_ordering='th',
           image_shape=None, filter_shape=None):
    '''
    Run on cuDNN if available.
    border_mode: string, "same" or "valid".
    dim_ordering: whether to use Theano or TensorFlow dimension ordering
    in inputs/kernels/ouputs.
    '''
    if border_mode == 'same':
        padding = 'SAME'
    elif border_mode == 'valid':
        padding = 'VALID'
    else:
        raise Exception('Invalid border mode: ' + str(border_mode))

    strides = (1,) + strides + (1,)

    if _FLOATX == 'float64':
        # tf conv2d only supports float32
        x = tfv1.cast(x, 'float32')
        kernel = tfv1.cast(kernel, 'float32')

    if dim_ordering == 'th':
        # TF uses the last dimension as channel dimension,
        # instead of the 2nd one.
        # TH input shape: (samples, input_depth, rows, cols)
        # TF input shape: (samples, rows, cols, input_depth)
        # TH kernel shape: (depth, input_depth, rows, cols)
        # TF kernel shape: (rows, cols, input_depth, depth)
        x = tfv1.transpose(x, (0, 2, 3, 1))
        kernel = tfv1.transpose(kernel, (2, 3, 1, 0))
        x = tfv1.nn.conv2d(x, kernel, strides, padding=padding)
        x = tfv1.transpose(x, (0, 3, 1, 2))
    elif dim_ordering == 'tf':
        x = tfv1.nn.conv2d(x, kernel, strides, padding=padding)
    else:
        raise Exception('Unknown dim_ordering: ' + str(dim_ordering))

    if _FLOATX == 'float64':
        x = tfv1.cast(x, 'float64')
    return x


def pool2d(x, pool_size, strides=(1, 1),
           border_mode='valid', dim_ordering='th', pool_mode='max'):
    '''
    pool_size: tuple of 2 integers.
    strides: tuple of 2 integers.
    border_mode: one of "valid", "same".
    dim_ordering: one of "th", "tf".
    '''
    if border_mode == 'same':
        padding = 'SAME'
    elif border_mode == 'valid':
        padding = 'VALID'
    else:
        raise Exception('Invalid border mode: ' + str(border_mode))

    strides = (1,) + strides + (1,)
    pool_size = (1,) + pool_size + (1,)

    if _FLOATX == 'float64':
        # tf max_pool only supports float32
        x = tfv1.cast(x, 'float32')

    if dim_ordering in {'tf', 'th'}:
        if dim_ordering == 'th':
            # TF uses the last dimension as channel dimension,
            # instead of the 2nd one.
            # TH input shape: (samples, input_depth, rows, cols)
            # TF input shape: (samples, rows, cols, input_depth)
            # TH kernel shape: (depth, input_depth, rows, cols)
            # TF kernel shape: (rows, cols, input_depth, depth)
            x = tfv1.transpose(x, (0, 2, 3, 1))
        if pool_mode == 'max':
            x = tfv1.nn.max_pool(x, pool_size, strides, padding=padding)
        elif pool_mode == 'avg':
            x = tfv1.nn.avg_pool(x, pool_size, strides, padding=padding)
        else:
            raise Exception('Invalid pooling mode: ' + str(pool_mode))
        if dim_ordering == 'th':
            x = tfv1.transpose(x, (0, 3, 1, 2))
    else:
        raise Exception('Unknown dim_ordering: ' + str(dim_ordering))

    if _FLOATX == 'float64':
        x = tfv1.cast(x, 'float64')
    return x


# RANDOMNESS

def random_normal(shape, mean=0.0, std=1.0, dtype=_FLOATX, seed=None):
    if seed is None:
        seed = np.random.randint(10e6)
    return tfv1.random_normal(shape, mean=mean, stddev=std,
                            dtype=dtype, seed=seed)


def random_uniform(shape, low=0.0, high=1.0, dtype=_FLOATX, seed=None):
    if seed is None:
        seed = np.random.randint(10e6)
    return tfv1.random_uniform(shape, minval=low, maxval=high,
                             dtype=dtype, seed=seed)
