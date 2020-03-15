import numpy as np
cimport numpy as np

cdef class _DataManager:
    """
    Manages the database.
    """

    # Internal structure
    cdef int   n_samples       # Number of samples
    cdef int   n_features      # Number of features
    cdef int   n_vacant        # Number of empty indices in the database
    cdef int** X               # Sample data
    cdef int*  y               # Label data
    cdef int*  f               # Features
    cdef int*  vacant          # Empty indices in the database

    # # Python API
    # cpdef int init(self, object X_in, np.ndarray y_in, np.ndarray f_in)

    # C API
    cdef int get_all_data(self, int*** X_ptr, int** y_ptr, int**f_ptr,
                          int* n_samples, int* n_features) nogil
    cdef int get_data(self, int* samples, int n_samples,
                      int ***X_sub_ptr, int **y_sub_ptr) nogil
    cdef int remove_data(self, int* samples, int n_samples) nogil