# discopt-soln
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

# Install Anaconda + Gurobi
* Download Anaconda install package from 
  [here](https://www.anaconda.com/download/)
* During installation, add Anaconda to PATH variable
* In terminal, run ```conda install -c gurobi gurobi```
* Apply for your free gurobi academic or online course license
  [here](http://www.gurobi.com/downloads/download-center)
* Run ```grbgetkey YOUR_KEY_ID``` on the computer to run gurobi

# Bottom Line
Feel free to read my code and clone this repo.  Suggestions and pull requests
will be much appreciated.  But when taking the course, please be HONEST and 
submit your own solution.
