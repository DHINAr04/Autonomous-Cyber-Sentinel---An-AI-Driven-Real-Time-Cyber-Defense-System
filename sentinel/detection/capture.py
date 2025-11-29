import os
import logging
from typing import Dict, Iterator, Optional
from sentinel.common.config import capture_iface

logger = logging.getLogger(__name__)


class LiveCapture:
    """Production-grade network packet capture with performance optimization."""
    
    def __init__(self, interface: Optional[str] = None, bpf_filter: str = "ip") -> None:
        self._iface = interface or capture_iface()
        self._bpf_filter = bpf_filter
        self._packet_count = 0
        self._error_count = 0
        
        logger.info(f"Initializing LiveCapture on interface: {self._iface}")
        self._validate_interface()

    def _validate_interface(self) -> None:
        """Validate network interface exists and is accessible."""
        try:
            from scapy.all import get_if_list
            available_ifaces = get_if_list()
            
            if self._iface not in available_ifaces:
                logger.warning(f"Interface {self._iface} not found. Available: {available_ifaces}")
                # Try to use first available interface
                if available_ifaces:
                    self._iface = available_ifaces[0]
                    logger.info(f"Using fallback interface: {self._iface}")
        except Exception as e:
            logger.error(f"Interface validation failed: {e}")

    def stream(self) -> Iterator[Dict[str, int | str | float]]:
        """Stream packets from network interface with error handling."""
        try:
            from scapy.all import sniff, conf
            from scapy.layers.inet import IP, TCP, UDP
            from scapy.layers.inet6 import IPv6
            
            # Optimize Scapy for production
            conf.use_pcap = True  # Use libpcap for better performance
            conf.sniff_promisc = True  # Promiscuous mode
            
            logger.info(f"Starting packet capture on {self._iface} with filter: {self._bpf_filter}")
            
        except ImportError as e:
            logger.error(f"Scapy import failed: {e}")
            return iter(())

        def _pkt_to_evt(pkt) -> Optional[Dict[str, int | str | float]]:
            """Convert packet to event dictionary with enhanced metadata."""
            try:
                self._packet_count += 1
                
                # Log progress every 1000 packets
                if self._packet_count % 1000 == 0:
                    logger.debug(f"Processed {self._packet_count} packets")
                
                # Handle IPv4
                if IP in pkt:
                    ip = pkt[IP]
                    proto = "tcp" if TCP in pkt else "udp" if UDP in pkt else str(ip.proto)
                    
                    # Extract ports if available
                    sport = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0)
                    dport = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0)
                    
                    # TCP flags if available
                    flags = str(pkt[TCP].flags) if TCP in pkt else ""
                    
                    return {
                        "src": ip.src,
                        "dst": ip.dst,
                        "proto": proto,
                        "sport": int(sport),
                        "dport": int(dport),
                        "size": int(len(pkt)),
                        "ts": float(getattr(pkt, "time", __import__("time").time())),
                        "flags": flags,
                        "ttl": int(ip.ttl) if hasattr(ip, 'ttl') else 0
                    }
                
                # Handle IPv6
                elif IPv6 in pkt:
                    ip = pkt[IPv6]
                    proto = "tcp" if TCP in pkt else "udp" if UDP in pkt else "ipv6"
                    
                    sport = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0)
                    dport = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0)
                    
                    return {
                        "src": ip.src,
                        "dst": ip.dst,
                        "proto": proto,
                        "sport": int(sport),
                        "dport": int(dport),
                        "size": int(len(pkt)),
                        "ts": float(getattr(pkt, "time", __import__("time").time())),
                        "flags": "",
                        "ttl": 0
                    }
                
                return None
                
            except Exception as e:
                self._error_count += 1
                if self._error_count % 100 == 0:
                    logger.error(f"Packet processing error (count: {self._error_count}): {e}")
                return None

        try:
            # Start sniffing with production settings
            for pkt in sniff(
                iface=self._iface,
                filter=self._bpf_filter,
                store=False,  # Don't store packets in memory
                prn=None  # Process inline for performance
            ):
                evt = _pkt_to_evt(pkt)
                if evt:
                    yield evt
                    
        except PermissionError:
            logger.error("Permission denied. Run with sudo/administrator privileges for packet capture.")
            raise
        except Exception as e:
            logger.error(f"Packet capture failed: {e}")
            raise

    def get_stats(self) -> Dict[str, int]:
        """Get capture statistics."""
        return {
            "packets_processed": self._packet_count,
            "errors": self._error_count
        }