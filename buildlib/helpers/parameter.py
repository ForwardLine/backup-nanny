import os

class Parameter(object):

    PARAMETER_KEY = 'ParameterKey'
    PARAMETER_VALUE = 'ParameterValue'
    USE_PREVIOUS_VALUE = 'UsePreviousValue'

    def __init__(self, parameter, use_previous_value):
        self.parameter = parameter
        self.use_previous_value = use_previous_value
        self.snake_parameter = None

    def get_dictionary(self):
        ret =  {
            self.PARAMETER_KEY: self.parameter,
            self.PARAMETER_VALUE: os.environ[self.snake_parameter],
        }
        if self.use_previous_value:
            ret.update({
                self.USE_PREVIOUS_VALUE: True,
            })
            ret.pop(self.PARAMETER_VALUE)
        return ret

    def has_environment_variable(self):
        self.snake_parameter = self.to_snake(self.parameter)
        return os.environ.get(self.snake_parameter, False)

    def to_snake(self, camel):
        return ''.join(['_{0}'.format(char) if char.isupper() else char.upper() for char in camel]).lstrip('_')
