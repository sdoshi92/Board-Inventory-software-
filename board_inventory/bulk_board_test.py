import requests
import sys
import json
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class BulkBoardCreationTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.test_category_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_boards = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def run_api_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_detail = response.json().get('detail', 'No error detail')
                    details += f", Error: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def setup_test_environment(self):
        """Setup test environment with user and category"""
        print("🔧 Setting up test environment...")
        
        # Register user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"bulk_test_user_{timestamp}@example.com"
        test_password = "BulkTest123!"
        
        result = self.run_api_test(
            "Setup - User Registration",
            "POST",
            "auth/register",
            200,
            data={"email": test_email, "password": test_password}
        )
        
        if result and 'access_token' in result:
            self.token = result['access_token']
            self.user_data = result['user']
        else:
            return False
        
        # Create test category
        category_data = {
            "name": f"Bulk Test Category {timestamp}",
            "description": "Category for bulk board creation testing",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        result = self.run_api_test(
            "Setup - Create Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if result and 'id' in result:
            self.test_category_id = result['id']
            return True
        return False

    def test_bulk_board_creation_sequential(self, count=10):
        """Test creating multiple boards sequentially with sequential serial numbers"""
        print(f"\n📦 Testing Sequential Bulk Board Creation ({count} boards)")
        print("-" * 60)
        
        if not self.test_category_id:
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        base_serial = f"BULK{timestamp}"
        created_boards = []
        
        start_time = time.time()
        
        for i in range(1, count + 1):
            serial_number = f"{base_serial}{i:04d}"  # e.g., BULK1234560001, BULK1234560002
            
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": serial_number,
                "location": "In stock",
                "condition": "New",
                "qc_by": "Bulk Test QC",
                "comments": f"Bulk creation test board {i} of {count}"
            }
            
            result = self.run_api_test(
                f"Bulk Sequential - Create Board {i:02d} ({serial_number})",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if result and 'id' in result:
                created_boards.append({
                    'id': result['id'],
                    'serial_number': serial_number,
                    'expected_data': board_data
                })
            else:
                self.log_test(f"Bulk Sequential Creation Failed at Board {i}", False, 
                    f"Failed to create board with serial {serial_number}")
                break
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Store created boards for cleanup
        self.created_boards.extend(created_boards)
        
        success = len(created_boards) == count
        details = f"Created {len(created_boards)}/{count} boards in {creation_time:.2f} seconds"
        if success:
            details += f" (avg {creation_time/count:.3f}s per board)"
        
        self.log_test(f"Bulk Sequential Creation Summary", success, details)
        return success

    def test_bulk_board_creation_concurrent(self, count=10):
        """Test creating multiple boards concurrently"""
        print(f"\n⚡ Testing Concurrent Bulk Board Creation ({count} boards)")
        print("-" * 60)
        
        if not self.test_category_id:
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        base_serial = f"CONC{timestamp}"
        
        def create_single_board(board_index):
            """Create a single board - used for concurrent execution"""
            serial_number = f"{base_serial}{board_index:04d}"
            
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": serial_number,
                "location": "In stock",
                "condition": "New",
                "qc_by": "Concurrent Test QC",
                "comments": f"Concurrent creation test board {board_index} of {count}"
            }
            
            url = f"{self.api_url}/boards"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            
            try:
                response = requests.post(url, json=board_data, headers=headers, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'board_index': board_index,
                        'serial_number': serial_number,
                        'board_id': result.get('id'),
                        'response': result
                    }
                else:
                    return {
                        'success': False,
                        'board_index': board_index,
                        'serial_number': serial_number,
                        'error': f"Status {response.status_code}: {response.text[:200]}"
                    }
            except Exception as e:
                return {
                    'success': False,
                    'board_index': board_index,
                    'serial_number': serial_number,
                    'error': str(e)
                }
        
        start_time = time.time()
        created_boards = []
        failed_boards = []
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all board creation tasks
            future_to_index = {
                executor.submit(create_single_board, i): i 
                for i in range(1, count + 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                result = future.result()
                
                if result['success']:
                    created_boards.append({
                        'id': result['board_id'],
                        'serial_number': result['serial_number'],
                        'board_index': result['board_index']
                    })
                    self.log_test(
                        f"Concurrent - Board {result['board_index']:02d} ({result['serial_number']})",
                        True,
                        "Created successfully"
                    )
                else:
                    failed_boards.append(result)
                    self.log_test(
                        f"Concurrent - Board {result['board_index']:02d} ({result['serial_number']})",
                        False,
                        result['error']
                    )
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Store created boards for cleanup
        self.created_boards.extend(created_boards)
        
        success = len(created_boards) == count
        details = f"Created {len(created_boards)}/{count} boards concurrently in {creation_time:.2f} seconds"
        if len(failed_boards) > 0:
            details += f", {len(failed_boards)} failed"
        
        self.log_test(f"Bulk Concurrent Creation Summary", success, details)
        return success

    def test_serial_number_duplicate_validation(self):
        """Test that duplicate serial numbers are properly rejected"""
        print(f"\n🔍 Testing Serial Number Duplicate Validation")
        print("-" * 60)
        
        if not self.test_category_id:
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        duplicate_serial = f"DUPLICATE{timestamp}"
        
        # Create first board with specific serial number
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": duplicate_serial,
            "location": "In stock",
            "condition": "New",
            "qc_by": "Duplicate Test QC",
            "comments": "First board for duplicate testing"
        }
        
        result1 = self.run_api_test(
            f"Duplicate Test - Create First Board ({duplicate_serial})",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not result1 or 'id' not in result1:
            return False
        
        # Store for cleanup
        self.created_boards.append({
            'id': result1['id'],
            'serial_number': duplicate_serial
        })
        
        # Try to create second board with same serial number - should fail
        board_data_duplicate = {
            "category_id": self.test_category_id,
            "serial_number": duplicate_serial,  # Same serial number
            "location": "In stock",
            "condition": "New",
            "qc_by": "Duplicate Test QC",
            "comments": "Second board for duplicate testing - should fail"
        }
        
        result2 = self.run_api_test(
            f"Duplicate Test - Create Duplicate Board (should fail)",
            "POST",
            "boards",
            400,  # Expecting 400 Bad Request
            data=board_data_duplicate
        )
        
        # Success means the duplicate was properly rejected (result2 should be None)
        success = result2 is None
        self.log_test(
            "Serial Number Duplicate Validation",
            success,
            "Duplicate serial number properly rejected" if success else "Duplicate serial number was not rejected"
        )
        
        return success

    def test_serial_number_edge_cases(self):
        """Test edge cases for serial number validation"""
        print(f"\n🎯 Testing Serial Number Edge Cases")
        print("-" * 60)
        
        if not self.test_category_id:
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        edge_cases = [
            {
                "name": "Leading Zeros",
                "serial": f"00{timestamp}001",
                "should_succeed": True
            },
            {
                "name": "Special Characters",
                "serial": f"EDGE-{timestamp}_001",
                "should_succeed": True
            },
            {
                "name": "Very Long Serial",
                "serial": f"VERYLONGSERIAL{timestamp}WITHMANYCHARS001",
                "should_succeed": True
            },
            {
                "name": "Numeric Only",
                "serial": f"{timestamp}001",
                "should_succeed": True
            }
        ]
        
        all_passed = True
        
        for case in edge_cases:
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": case["serial"],
                "location": "In stock",
                "condition": "New",
                "comments": f"Edge case test: {case['name']}"
            }
            
            expected_status = 200 if case["should_succeed"] else 400
            result = self.run_api_test(
                f"Edge Case - {case['name']} ({case['serial']})",
                "POST",
                "boards",
                expected_status,
                data=board_data
            )
            
            if case["should_succeed"] and result and 'id' in result:
                # Store for cleanup
                self.created_boards.append({
                    'id': result['id'],
                    'serial_number': case["serial"]
                })
            elif not case["should_succeed"] and result is None:
                # Expected failure
                pass
            else:
                all_passed = False
        
        return all_passed

    def test_data_integrity_verification(self):
        """Verify all created boards have correct data integrity"""
        print(f"\n🔍 Testing Data Integrity Verification")
        print("-" * 60)
        
        if not self.created_boards:
            self.log_test("Data Integrity - No Boards to Verify", False, "No boards were created in previous tests")
            return False
        
        # Get all boards from API
        all_boards_result = self.run_api_test(
            "Data Integrity - Get All Boards",
            "GET",
            "boards",
            200
        )
        
        if not all_boards_result or not isinstance(all_boards_result, list):
            return False
        
        # Verify each created board
        verified_count = 0
        integrity_issues = []
        
        for created_board in self.created_boards:
            # Find the board in API response
            api_board = next(
                (board for board in all_boards_result if board['id'] == created_board['id']),
                None
            )
            
            if not api_board:
                integrity_issues.append(f"Board {created_board['serial_number']} not found in API response")
                continue
            
            # Verify basic data integrity
            checks = [
                ("ID matches", api_board['id'] == created_board['id']),
                ("Serial number matches", api_board['serial_number'] == created_board['serial_number']),
                ("Category ID correct", api_board['category_id'] == self.test_category_id),
                ("Location is In stock", api_board['location'] == "In stock"),
                ("Has created_at timestamp", 'created_at' in api_board and api_board['created_at']),
                ("Has created_by field", 'created_by' in api_board and api_board['created_by']),
                ("Has inward_date_time", 'inward_date_time' in api_board and api_board['inward_date_time'])
            ]
            
            board_passed = True
            for check_name, check_result in checks:
                if not check_result:
                    integrity_issues.append(f"Board {created_board['serial_number']}: {check_name} failed")
                    board_passed = False
            
            if board_passed:
                verified_count += 1
                self.log_test(
                    f"Data Integrity - Board {created_board['serial_number']}",
                    True,
                    "All integrity checks passed"
                )
        
        success = verified_count == len(self.created_boards) and len(integrity_issues) == 0
        details = f"Verified {verified_count}/{len(self.created_boards)} boards"
        if integrity_issues:
            details += f", Issues: {'; '.join(integrity_issues[:3])}"  # Show first 3 issues
        
        self.log_test("Data Integrity Verification Summary", success, details)
        return success

    def test_performance_metrics(self):
        """Test and measure performance metrics for bulk operations"""
        print(f"\n📊 Testing Performance Metrics")
        print("-" * 60)
        
        batch_sizes = [5, 10, 20]
        performance_results = []
        
        for batch_size in batch_sizes:
            timestamp = datetime.now().strftime('%H%M%S%f')[:-3]  # Include milliseconds
            base_serial = f"PERF{timestamp}"
            
            start_time = time.time()
            created_count = 0
            
            for i in range(1, batch_size + 1):
                board_data = {
                    "category_id": self.test_category_id,
                    "serial_number": f"{base_serial}{i:03d}",
                    "location": "In stock",
                    "condition": "New",
                    "comments": f"Performance test batch {batch_size}, board {i}"
                }
                
                result = self.run_api_test(
                    f"Performance Batch {batch_size} - Board {i:02d}",
                    "POST",
                    "boards",
                    200,
                    data=board_data
                )
                
                if result and 'id' in result:
                    created_count += 1
                    # Store for cleanup
                    self.created_boards.append({
                        'id': result['id'],
                        'serial_number': f"{base_serial}{i:03d}"
                    })
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time_per_board = total_time / created_count if created_count > 0 else 0
            
            performance_results.append({
                'batch_size': batch_size,
                'created_count': created_count,
                'total_time': total_time,
                'avg_time_per_board': avg_time_per_board,
                'boards_per_second': created_count / total_time if total_time > 0 else 0
            })
            
            success = created_count == batch_size
            details = f"Created {created_count}/{batch_size} boards in {total_time:.2f}s (avg {avg_time_per_board:.3f}s/board, {created_count/total_time:.1f} boards/s)"
            
            self.log_test(f"Performance Test - Batch Size {batch_size}", success, details)
        
        # Summary of performance results
        if performance_results:
            best_performance = max(performance_results, key=lambda x: x['boards_per_second'])
            summary = f"Best performance: {best_performance['boards_per_second']:.1f} boards/s (batch size {best_performance['batch_size']})"
            self.log_test("Performance Testing Summary", True, summary)
        
        return len(performance_results) == len(batch_sizes)

    def test_error_handling_scenarios(self):
        """Test error handling in bulk operations"""
        print(f"\n⚠️  Testing Error Handling Scenarios")
        print("-" * 60)
        
        if not self.test_category_id:
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Test 1: Invalid category ID
        invalid_board_data = {
            "category_id": "invalid-category-id",
            "serial_number": f"ERROR{timestamp}001",
            "location": "In stock",
            "condition": "New"
        }
        
        result1 = self.run_api_test(
            "Error Handling - Invalid Category ID",
            "POST",
            "boards",
            400,
            data=invalid_board_data
        )
        
        # Test 2: Missing required fields
        incomplete_board_data = {
            "category_id": self.test_category_id,
            # Missing serial_number
            "location": "In stock"
        }
        
        result2 = self.run_api_test(
            "Error Handling - Missing Serial Number",
            "POST",
            "boards",
            422,  # Unprocessable Entity for validation errors
            data=incomplete_board_data
        )
        
        # Test 3: Invalid condition value
        invalid_condition_data = {
            "category_id": self.test_category_id,
            "serial_number": f"ERROR{timestamp}003",
            "location": "In stock",
            "condition": "InvalidCondition"
        }
        
        result3 = self.run_api_test(
            "Error Handling - Invalid Condition",
            "POST",
            "boards",
            200,  # API might accept any string for condition
            data=invalid_condition_data
        )
        
        if result3 and 'id' in result3:
            # Clean up if it was created
            self.created_boards.append({
                'id': result3['id'],
                'serial_number': f"ERROR{timestamp}003"
            })
        
        # Test 4: Very long serial number
        long_serial_data = {
            "category_id": self.test_category_id,
            "serial_number": f"VERYLONGSERIAL{timestamp}" + "X" * 100,  # Very long serial
            "location": "In stock",
            "condition": "New"
        }
        
        result4 = self.run_api_test(
            "Error Handling - Very Long Serial Number",
            "POST",
            "boards",
            200,  # Might be accepted depending on DB constraints
            data=long_serial_data
        )
        
        if result4 and 'id' in result4:
            # Clean up if it was created
            self.created_boards.append({
                'id': result4['id'],
                'serial_number': long_serial_data['serial_number']
            })
        
        # Count successful error handling (where we expected failures and got them)
        expected_failures = [result1, result2]  # These should be None (failed as expected)
        successful_error_handling = sum(1 for result in expected_failures if result is None)
        
        success = successful_error_handling >= 1  # At least some error handling works
        details = f"Properly handled {successful_error_handling}/2 expected error scenarios"
        
        self.log_test("Error Handling Summary", success, details)
        return success

    def cleanup_created_boards(self):
        """Clean up all boards created during testing"""
        print(f"\n🧹 Cleaning up created boards...")
        print("-" * 60)
        
        if not self.created_boards:
            self.log_test("Cleanup - No boards to clean up", True, "No boards were created")
            return True
        
        cleanup_count = 0
        failed_cleanup = []
        
        for board in self.created_boards:
            result = self.run_api_test(
                f"Cleanup - Delete Board {board['serial_number']}",
                "DELETE",
                f"boards/{board['id']}",
                200
            )
            
            if result is not None:
                cleanup_count += 1
            else:
                failed_cleanup.append(board['serial_number'])
        
        success = cleanup_count == len(self.created_boards)
        details = f"Cleaned up {cleanup_count}/{len(self.created_boards)} boards"
        if failed_cleanup:
            details += f", Failed: {', '.join(failed_cleanup[:5])}"  # Show first 5 failures
        
        self.log_test("Cleanup Summary", success, details)
        
        # Clean up category
        if self.test_category_id:
            self.run_api_test(
                "Cleanup - Delete Test Category",
                "DELETE",
                f"categories/{self.test_category_id}",
                200
            )
        
        return success

    def run_all_bulk_tests(self):
        """Run all bulk board creation tests"""
        print("🚀 Starting Bulk Board Creation Tests")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        # Run all tests
        test_methods = [
            (self.test_bulk_board_creation_sequential, 10),
            (self.test_bulk_board_creation_concurrent, 10),
            (self.test_serial_number_duplicate_validation,),
            (self.test_serial_number_edge_cases,),
            (self.test_data_integrity_verification,),
            (self.test_performance_metrics,),
            (self.test_error_handling_scenarios,)
        ]
        
        for test_method_info in test_methods:
            if len(test_method_info) > 1:
                test_method, *args = test_method_info
                test_method(*args)
            else:
                test_method_info[0]()
        
        # Cleanup
        self.cleanup_created_boards()
        
        # Final summary
        print("\n" + "=" * 80)
        print(f"📊 Final Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All bulk board creation tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = BulkBoardCreationTester()
    success = tester.run_all_bulk_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()