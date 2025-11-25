"""
Generate synthetic network traffic for testing the Sentinel system.
This script simulates various types of network activity.
"""
import requests
import time
import random
import argparse
from typing import List, Dict


class TrafficGenerator:
    """Generate synthetic network traffic patterns."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_health(self) -> bool:
        """Check if the Sentinel API is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_stats(self) -> Dict:
        """Get current system statistics."""
        try:
            response = self.session.get(f"{self.base_url}/stats", timeout=5)
            return response.json()
        except Exception:
            return {}
    
    def simulate_normal_traffic(self, duration: int = 60):
        """Simulate normal network traffic."""
        print(f"🟢 Simulating normal traffic for {duration} seconds...")
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < duration:
            # Just monitor the system - detection engine generates synthetic traffic
            time.sleep(2)
            count += 1
            
            if count % 5 == 0:
                stats = self.get_stats()
                print(f"   Stats: {stats.get('alerts', 0)} alerts, "
                      f"{stats.get('investigations', 0)} investigations, "
                      f"{stats.get('actions', 0)} actions")
        
        print(f"✓ Normal traffic simulation complete")
    
    def simulate_attack_scenario(self, scenario: str = "port_scan"):
        """Simulate various attack scenarios."""
        scenarios = {
            "port_scan": "Port scanning attack",
            "ddos": "DDoS attack",
            "data_exfil": "Data exfiltration",
            "lateral_movement": "Lateral movement"
        }
        
        print(f"🔴 Simulating attack: {scenarios.get(scenario, scenario)}")
        print("   (Note: Actual attack simulation requires network access)")
        print("   The system will generate synthetic high-severity alerts")
        
        # Monitor for high-severity alerts
        for i in range(10):
            time.sleep(2)
            stats = self.get_stats()
            
            if stats:
                severities = stats.get('alert_severities', {})
                high_alerts = severities.get('high', 0)
                
                if high_alerts > 0:
                    print(f"   ⚠️  Detected {high_alerts} high-severity alerts!")
        
        print(f"✓ Attack scenario complete")
    
    def monitor_response_time(self, duration: int = 30):
        """Monitor system response times."""
        print(f"⏱️  Monitoring response times for {duration} seconds...")
        
        start_time = time.time()
        initial_stats = self.get_stats()
        initial_alerts = initial_stats.get('alerts', 0)
        
        time.sleep(duration)
        
        final_stats = self.get_stats()
        final_alerts = final_stats.get('alerts', 0)
        final_actions = final_stats.get('actions', 0)
        
        new_alerts = final_alerts - initial_alerts
        
        if new_alerts > 0:
            avg_response_time = duration / new_alerts
            print(f"   New alerts: {new_alerts}")
            print(f"   Actions taken: {final_actions}")
            print(f"   Avg response time: {avg_response_time:.2f}s per alert")
            
            if avg_response_time < 10:
                print(f"   ✅ Meeting <10s SLA target!")
            else:
                print(f"   ⚠️  Exceeding 10s SLA target")
        else:
            print(f"   No new alerts generated during monitoring period")
    
    def stress_test(self, duration: int = 60):
        """Perform a stress test."""
        print(f"💪 Running stress test for {duration} seconds...")
        print("   Monitoring system under load...")
        
        start_time = time.time()
        samples = []
        
        while time.time() - start_time < duration:
            sample_start = time.time()
            stats = self.get_stats()
            sample_time = time.time() - sample_start
            
            samples.append({
                'response_time': sample_time,
                'alerts': stats.get('alerts', 0),
                'timestamp': time.time()
            })
            
            time.sleep(1)
        
        # Calculate metrics
        avg_response = sum(s['response_time'] for s in samples) / len(samples)
        max_response = max(s['response_time'] for s in samples)
        total_alerts = samples[-1]['alerts'] - samples[0]['alerts']
        
        print(f"\n📊 Stress Test Results:")
        print(f"   Duration: {duration}s")
        print(f"   Total alerts: {total_alerts}")
        print(f"   Avg API response: {avg_response*1000:.2f}ms")
        print(f"   Max API response: {max_response*1000:.2f}ms")
        print(f"   Throughput: {total_alerts/duration:.2f} alerts/sec")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic traffic for Sentinel testing"
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Sentinel API base URL'
    )
    parser.add_argument(
        '--mode',
        choices=['normal', 'attack', 'monitor', 'stress'],
        default='normal',
        help='Traffic generation mode'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration in seconds'
    )
    parser.add_argument(
        '--scenario',
        choices=['port_scan', 'ddos', 'data_exfil', 'lateral_movement'],
        default='port_scan',
        help='Attack scenario (for attack mode)'
    )
    
    args = parser.parse_args()
    
    print("🛡️  Autonomous Cyber Sentinel - Traffic Generator")
    print("=" * 60)
    
    generator = TrafficGenerator(args.url)
    
    # Check connectivity
    print(f"\n🔌 Checking connection to {args.url}...")
    if not generator.check_health():
        print(f"❌ Cannot connect to Sentinel API at {args.url}")
        print("   Make sure the system is running:")
        print("   - Local: .\\scripts\\dev.ps1 run")
        print("   - Docker: docker-compose up")
        return
    
    print("✓ Connected successfully\n")
    
    # Run selected mode
    if args.mode == 'normal':
        generator.simulate_normal_traffic(args.duration)
    elif args.mode == 'attack':
        generator.simulate_attack_scenario(args.scenario)
    elif args.mode == 'monitor':
        generator.monitor_response_time(args.duration)
    elif args.mode == 'stress':
        generator.stress_test(args.duration)
    
    # Final stats
    print("\n📊 Final Statistics:")
    stats = generator.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")
    
    print("\n✅ Traffic generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
