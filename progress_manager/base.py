"""This module contains the BaseExtension class which Base class for all extensions.


"""
import abc


class BaseExtension(object, metaclass = abc.ABCMeta):
    """Base class for all extensions.

    All extensions need to inherit from this class. Before calling any
    method of an extension, It is explicitly checked whether it inherits
    from this class. This class provides various methods which can be
    overidden to achieve desired behaviour.

    Parameters
    ----------
    requirements : array_like
        Keys whose value, the extension needs.

    Notes
    -----
    All extensions need to explicitly call __init__ of the BaseExtension with
    appropriate requirements. If an extension inherits from another extension,
    __init__ should be called like BaseExtension.__init__(self, requirements)
    """
    @abc.abstractmethod
    def __init__(self, requirements = [], update_interval=None):
        self._value = None
        self._requirements = requirements
        self._update_interval = update_interval

    def get_requirements(self):
        """Get the requirements of the extension.

        Returns
        -------
        array_like:
            requirements of the extension.

        Notes
        -----
        Never Override this method.
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

        Notes
        -----
        Never Override this method.
        """
        self._value = value

    def get_value(self):
        """Get the current value to be printed to console.

        Returns
        -------
        str
            value set by `set_value`

        Notes
        -----
        Never Override this method.
        """
        return self._value

    def _on_begin(self, params):
        """Override this method to customize the initial look of the extension.

        By default, the appropriate after-validation method is called.

        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        self._on_update(params)

    def _on_update(self, params):
        """Override this method to set the look of the extension at each update.

        This method is called at each update. It is recommended to override the
        higher level functions `_on_validated` and `_on_invalidated` instead of
        this method.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        if self._validate(params):
            self._on_validated(params)
        else:
            self._on_invalidated(params)

    def _on_end(self, params):
        """Override this method to customize the final look of the extension.

        By default, the appropriate after-validation method is called.

        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        self._on_update(params)

    def _on_validated(self, params):
        """Override this method to set the look of the extension at each update.

        This method is only called during an update if value of all keys in
        requirements are valid.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        pass

    def _on_invalidated(self, params):
        """Override this method to set the look of the extension at each update.

        This method is only called during an update if value for atleast one key
        in requirements is invalid.
        
        Parameters
        ----------
        params : array_like
            Values of all keys specified in the requirements of the extension.
        """
        pass

class BaseProvider(object, metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, tag, requirements = []):
        self._value = None
        self._requirements = requirements
        self._tag = tag

    def get_requirements(self):
        return self._requirements

    def get_tag(self):
        return self._tag

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def _is_update_required(self):
        return True

    def _on_begin(self, params):
        self._on_publish(params)

    def _on_publish(self, params):
        if self._validate(params):
            self._on_validated(params)
        else:
            self._on_invalidated(params)

    def _on_end(self, params):
        self._on_publish(params)

    def _validate(self, params):
        return (None not in params)

    def _on_validated(self, params):
        pass

    def _on_invalidated(self, params):
        self.set_value(None)
    
