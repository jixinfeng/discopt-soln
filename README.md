# discopt-soln-2016
My solutions for 
[discrete optimization](https://www.coursera.org/learn/discrete-optimization/)
course on Coursera

# Assignment Grade
* Week 01: 10/10
* Week 02: 60/60
* Week 03: 42/60

# Install CVXOPT + GLPK on macOS
* Install homebrew from [here](http://brew.sh)
* Install GLPK using homebrew: ```$ brew install glpk```
* Download CVXOPT source code from [here](http://cvxopt.org)
* Edit setup.py in CVXOPT source directory, turn ```BUILD_GLPK = 0``` to ```1```
    * Some time the ```GLPK_LIB_DIR``` and ```GLPK_INC_DIR``` should be
      corrected
* Install CVXOPT: ```$ python3 setup.py install```

# Bottom Line
Feel free to read my code and clone this repo.  Suggestions and pull requests
will be much appreciated.  But when taking the course, please be HONEST and 
submit your own solution.
