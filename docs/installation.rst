Installation
============

This guide will help you install and set up the ApexSigma DevEnviro project.

Prerequisites
-------------

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

Quick Start
-----------

1. **Clone the repository:**

.. code-block:: bash

   git clone https://github.com/ApexSigma-Solutions/apexsigma-devenviro.git
   cd apexsigma-devenviro

2. **Create and activate virtual environment:**

.. code-block:: bash

   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate

3. **Install dependencies:**

.. code-block:: bash

   pip install -r requirements.txt

Development Setup
-----------------

For development work, install additional development dependencies:

.. code-block:: bash

   pip install -r requirements-dev.txt

This includes:

- Testing frameworks (pytest, pytest-cov)
- Code quality tools (black, flake8, mypy)
- Documentation tools (sphinx)
- Security scanning (detect-secrets)

Environment Variables
---------------------

Create a `.env` file in `config/secrets/.env`:

.. code-block:: bash

   GEMINI_API_KEY=your_gemini_api_key_here
   LINEAR_API_KEY=your_linear_api_key_here
   QDRANT_URL=http://localhost:6333

**Important:** Never commit the `.env` file to version control. It's already included in `.gitignore`.

Verification
------------

Test your installation:

.. code-block:: bash

   # Test Gemini memory engine
   python code/test_mem0.py
   
   # Test DevEnviro startup
   python devenviro_startup.py
   
   # Quick task status
   python quick_tasks.py

These should run without errors if everything is set up correctly.

Docker Setup (Optional)
------------------------

If you prefer using Docker:

.. code-block:: bash

   # Build the image
   docker build -t apexsigma-devenviro .
   
   # Run the container
   docker run -it apexsigma-devenviro

Troubleshooting
---------------

**Common Issues:**

1. **Python version compatibility:**
   - Ensure you're using Python 3.10 or higher
   - Some dependencies require specific Python versions

2. **Missing dependencies:**
   - Run `pip install -r requirements.txt` again
   - Check for any error messages during installation

3. **Environment variables:**
   - Verify your `.env` file is in the project root
   - Ensure API keys are valid and properly formatted

**Getting Help:**

- Check the project's GitHub Issues page
- Review the documentation at the project URL
- Contact the development team