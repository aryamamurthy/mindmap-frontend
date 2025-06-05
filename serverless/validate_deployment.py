#!/usr/bin/env python3
"""
Deployment validation script for Mind Map serverless application.
Verifies configuration and dependencies before deployment.
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (NOT FOUND)")
        return False

def check_yaml_syntax(file_path):
    """Check YAML syntax."""
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        print(f"✓ YAML syntax valid: {file_path}")
        return True
    except yaml.YAMLError as e:
        print(f"✗ YAML syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading {file_path}: {e}")
        return False

def check_python_imports(file_path):
    """Check if Python file can be imported without errors."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Basic syntax check
        compile(content, file_path, 'exec')
        print(f"✓ Python syntax valid: {file_path}")
        return True
    except SyntaxError as e:
        print(f"✗ Python syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {file_path}: {e}")
        return False

def check_serverless_framework():
    """Check if Serverless Framework is installed."""
    try:
        result = subprocess.run(['serverless', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Serverless Framework installed: {version}")
            return True
        else:
            print(f"✗ Serverless Framework error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Serverless Framework check timed out")
        return False
    except FileNotFoundError:
        print("✗ Serverless Framework not found. Install with: npm install -g serverless")
        return False
    except Exception as e:
        print(f"✗ Error checking Serverless Framework: {e}")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print(f"✓ AWS credentials configured for account: {identity.get('Account', 'Unknown')}")
            return True
        else:
            print(f"✗ AWS credentials error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ AWS credentials check timed out")
        return False
    except FileNotFoundError:
        print("✗ AWS CLI not found. Install AWS CLI and configure credentials")
        return False
    except json.JSONDecodeError:
        print("✗ Invalid AWS CLI response")
        return False
    except Exception as e:
        print(f"✗ Error checking AWS credentials: {e}")
        return False

def main():
    """Main validation function."""
    print("=" * 60)
    print("Mind Map Serverless Application - Deployment Validation")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check core configuration files
    print("\n1. Configuration Files:")
    config_files = [
        ("serverless.yml", "Serverless Framework configuration"),
        ("requirements.txt", "Python dependencies"),
        (".gitignore", "Git ignore file (optional)")
    ]
    
    for file_path, description in config_files:
        if file_path == ".gitignore":
            check_file_exists(file_path, description)  # Optional
        else:
            if not check_file_exists(file_path, description):
                all_checks_passed = False
    
    # Check YAML syntax
    print("\n2. YAML Syntax:")
    if os.path.exists("serverless.yml"):
        if not check_yaml_syntax("serverless.yml"):
            all_checks_passed = False
    
    # Check Lambda handlers
    print("\n3. Lambda Handlers:")
    handler_dir = Path("lambda_handlers")
    if handler_dir.exists():
        handler_files = list(handler_dir.glob("*_handler.py"))
        if handler_files:
            for handler_file in handler_files:
                if not check_python_imports(str(handler_file)):
                    all_checks_passed = False
        else:
            print("✗ No Lambda handler files found in lambda_handlers/")
            all_checks_passed = False
    else:
        print("✗ lambda_handlers directory not found")
        all_checks_passed = False
    
    # Check utility files
    print("\n4. Utility Files:")
    utils_files = [
        "lambda_handlers/utils/__init__.py",
        "lambda_handlers/utils/logger.py"
    ]
    
    for utils_file in utils_files:
        if not check_file_exists(utils_file, f"Utils: {utils_file}"):
            all_checks_passed = False
        elif not check_python_imports(utils_file):
            all_checks_passed = False
    
    # Check external dependencies
    print("\n5. External Dependencies:")
    if not check_serverless_framework():
        all_checks_passed = False
    
    if not check_aws_credentials():
        all_checks_passed = False
    
    # Check documentation
    print("\n6. Documentation:")
    doc_files = [
        "COMPLETE_DOCUMENTATION.md",
        "API_REFERENCE.md",
        "DEPLOYMENT_OPERATIONS_GUIDE.md",
        "LOGGING_STRATEGY.md"
    ]
    
    for doc_file in doc_files:
        check_file_exists(doc_file, f"Documentation: {doc_file}")
    
    # Final result
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✓ ALL CRITICAL CHECKS PASSED - Ready for deployment!")
        print("\nNext steps:")
        print("1. Review environment variables in serverless.yml")
        print("2. Deploy to dev: serverless deploy --stage dev")
        print("3. Run integration tests")
        print("4. Deploy to production: serverless deploy --stage prod")
    else:
        print("✗ SOME CHECKS FAILED - Please fix issues before deployment")
        print("\nRecommended actions:")
        print("1. Fix all critical errors marked with ✗")
        print("2. Run this script again")
        print("3. Test locally if possible")
    print("=" * 60)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
