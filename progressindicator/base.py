"""This module contains the BaseExtension and BaseProvider class."""
import abc


class BaseExtension(object, metaclass = abc.ABCMeta):
    """Base class for all extensions.

    All extensions must inherit from this class. This class provides various
    methods which can be overidden to achieve desired behaviour.

    Parameters
    ----------
    requirements : array_like
        iterable of strings where each string should be a built-in tag or a tag
        provided by a registered custom provider.

    update_interval : float
        Desired update interval for the extension.

    Notes
    -----
    All extensions need to explicitly call __init__ of the BaseExtension with
    appropriate requirements. If an extension inherits from another extension,
    __init__ should be called like BaseExtension.__init__(self, requirements)
    """
    @abc.abstractmethod
    def __init__(self, requirements, update_interval=None):
        self._value = None
        self._requirements = requirements
        self._update_interval = update_interval

    def get_requirements(self):
        """Get the requirements of the extension.

        Returns
        -------
        array_like:
            list of tags required by the extension.
        """
        return self._requirements

    def _get_update_interval(self):
        return self._update_interval

    def _is_update_required(self, prev_params, params):
        """Override this method to explicity update the ProgressManager
        instance.

        Parameters
        ----------
        prev_params : array_like
            Values of all keys specified in the requirements of the extension
            when the extension was last updated.

        params : array_like
            Values of all keys specified in the requirements of the extension.

        Returns
        -------
        bool:
            True if update is required, else False

        Notes
        -----
        ProgressManager instance is updated by default every second
        automatically. Only return True when you want updates more frequently.
        You should not return True very often from this method. This method is
        called everytime publish is called which may lead to output being printed
        console on every call to publish and I/O operations are slow.
        """
        return False

    def _validate(self, params):
        """Checks whether params contains None.

        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        return (None not in params)

    def set_value(self, value):
        """This method sets the content which is to be printed to console.

        Parameters
        ----------
        value : str
            Value to be set.
        """
        self._value = value

    def get_value(self):
        """Get the current value to be printed to console.

        Returns
        -------
        str
            value set by `set_value`
        """
        return self._value

    def on_begin(self, params):
        """Override this method to customize the initial look of the extension.

        By default, the appropriate after-validation method is called.

        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        self.on_update(params)

    def on_update(self, params):
        """Override this method to set the look of the extension at each update.

        This method is called at each update. It is recommended to override the
        higher level functions `on_validated` and `on_invalidated` instead of
        this method.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        if self._validate(params):
            self.on_validated(params)
        else:
            self.on_invalidated(params)

    def on_end(self, params):
        """Override this method to customize the final look of the extension.

        By default, the appropriate after-validation method is called.

        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        self.on_update(params)

    def on_validated(self, params):
        """Override this method to set the look of the extension at each update.

        This method is only called during an update if value of all tags
        required by the extension are valid.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        pass

    def on_invalidated(self, params):
        """Override this method to set the look of the extension at each update.

        This method is only called during an update if value for atleast one
        tag required by the extension is invalid.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        pass

class BaseProvider(object, metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, tag, requirements):
        self._value = None
        self._requirements = requirements
        self._tag = tag

    def get_requirements(self):
        """Get the requirements of the extension.

        Returns
        -------
        array_like:
            requirements of the extension.
        """
        return self._requirements

    def get_tag(self):
        """Return the `tag` of the Provider.

        Returns
        -------
        str:
            `tag` of the provider.
        """
        return self._tag

    def set_value(self, value):
        """This method sets the value of the tag provided by the provider.

        Parameters
        ----------
        value : str
            Value to be set.
        """
        self._value = value

    def get_value(self):
        """Get the current value of the provider's tag.

        Returns
        -------
        str
            value set by `set_value`
        """
        return self._value

    def on_begin(self, params):
        """Override this method to set the initial value for the provider.

        By default, the appropriate after-validation method is called.

        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        self.on_publish(params)

    def on_publish(self, params):
        """Override this method to calculate the value for the provider at each
        publish.

        This method is called on every publish. It is recommended to override the
        higher level functions `on_validated` and `on_invalidated` instead of
        this method.
        
        Parameters
        ----------
        params : array_like
            Values of all tags specified in the requirements of the extension.
        """
        if self._validate(params):
            self.on_validated(params)
        else:
            self.on_invalidated(params)

    def on_end(self, params):
        """Override this method to calculate the final value for the provider.

        By default, the appropriate after-validation method is called.

        Parameters
        ----------
        params : array_like
            Values of all tags specified in the requirements of the extension.
        """
        self.on_publish(params)

    def _validate(self, params):
        return (None not in params)

    def on_validated(self, params):
        """Override this method to calculate the value for the provider at each
        publish.

        This method is only called during an update if value of all keys in
        requirements are valid.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        pass

    def on_invalidated(self, params):
        """Override this method to calculate the value for the provider at each
        publish.

        This method is only called during an update if value for atleast one key
        in requirements is invalid.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        self.set_value(None)
    
