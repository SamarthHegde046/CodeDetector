#!/usr/bin/env python3
"""
Web Scraping Utility - AI Generated Code
This module provides a comprehensive web scraping framework with rate limiting,
error handling, and data export capabilities.
Author: AI Assistant
Version: 1.0
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import random
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Union, Any
import logging
from dataclasses import dataclass
import re
from datetime import datetime
import os

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_scraper.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ScrapingConfig:
    """
    Configuration class for web scraping parameters.
    This dataclass encapsulates all scraping settings in a clean, organized manner.
    """
    base_url: str
    headers: Dict[str, str]
    delay_min: float = 1.0
    delay_max: float = 3.0
    timeout: int = 30
    max_retries: int = 3
    respect_robots: bool = True
    user_agent: str = "AI-WebScraper/1.0"

class WebScraper:
    """
    A comprehensive web scraping class that provides robust scraping capabilities
    with built-in error handling, rate limiting, and data export features.
    
    This class follows best practices for web scraping including:
    - Respectful rate limiting
    - Comprehensive error handling
    - Multiple export formats
    - Session management for efficiency
    """
    
    def __init__(self, config: ScrapingConfig):
        """
        Initialize the WebScraper with configuration settings.
        
        Args:
            config (ScrapingConfig): Configuration object containing scraping parameters
        """
        self.config = config
        self.session = requests.Session()
        self.scraped_data = []
        self.failed_urls = []
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': config.user_agent,
            **config.headers
        })
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("WebScraper initialized successfully")
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make a HTTP request with retry logic and error handling.
        
        Args:
            url (str): URL to request
            
        Returns:
            Optional[requests.Response]: Response object or None if failed
        """
        for attempt in range(self.config.max_retries):
            try:
                # Add random delay to be respectful to servers
                delay = random.uniform(self.config.delay_min, self.config.delay_max)
                time.sleep(delay)
                
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    allow_redirects=True
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                self.logger.info(f"Successfully scraped: {url}")
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    self.logger.error(f"All attempts failed for {url}")
                    self.failed_urls.append(url)
                    return None
                
                # Exponential backoff for retries
                time.sleep(2 ** attempt)
        
        return None
    
    def _parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html_content (str): Raw HTML content
            
        Returns:
            BeautifulSoup: Parsed HTML object
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def _extract_text_content(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract text content based on CSS selectors.
        
        Args:
            soup (BeautifulSoup): Parsed HTML object
            selectors (Dict[str, str]): Dictionary mapping field names to CSS selectors
            
        Returns:
            Dict[str, Any]: Extracted data
        """
        extracted_data = {}
        
        for field_name, selector in selectors.items():
            try:
                elements = soup.select(selector)
                
                if not elements:
                    extracted_data[field_name] = None
                    continue
                
                # Handle multiple elements vs single element
                if len(elements) == 1:
                    text_content = elements[0].get_text(strip=True)
                    extracted_data[field_name] = text_content if text_content else None
                else:
                    # Multiple elements - return list
                    text_list = []
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text:
                            text_list.append(text)
                    extracted_data[field_name] = text_list if text_list else None
                    
            except Exception as e:
                self.logger.warning(f"Error extracting {field_name} with selector {selector}: {str(e)}")
                extracted_data[field_name] = None
        
        return extracted_data
    
    def _extract_attributes(self, soup: BeautifulSoup, attr_selectors: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Extract element attributes based on CSS selectors.
        
        Args:
            soup (BeautifulSoup): Parsed HTML object
            attr_selectors (Dict[str, Dict[str, str]]): Nested dict with field names, selectors, and attributes
            
        Returns:
            Dict[str, Any]: Extracted attribute data
        """
        extracted_attrs = {}
        
        for field_name, config in attr_selectors.items():
            selector = config.get('selector')
            attribute = config.get('attribute')
            
            if not selector or not attribute:
                continue
            
            try:
                elements = soup.select(selector)
                
                if not elements:
                    extracted_attrs[field_name] = None
                    continue
                
                if len(elements) == 1:
                    attr_value = elements[0].get(attribute)
                    extracted_attrs[field_name] = attr_value
                else:
                    # Multiple elements
                    attr_list = []
                    for element in elements:
                        attr_value = element.get(attribute)
                        if attr_value:
                            attr_list.append(attr_value)
                    extracted_attrs[field_name] = attr_list if attr_list else None
                    
            except Exception as e:
                self.logger.warning(f"Error extracting attribute {field_name}: {str(e)}")
                extracted_attrs[field_name] = None
        
        return extracted_attrs
    
    def scrape_page(self, url: str, text_selectors: Dict[str, str] = None, 
                   attr_selectors: Dict[str, Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """
        Scrape a single page and extract specified data.
        
        Args:
            url (str): URL to scrape
            text_selectors (Dict[str, str]): CSS selectors for text extraction
            attr_selectors (Dict[str, Dict[str, str]]): CSS selectors for attribute extraction
            
        Returns:
            Optional[Dict[str, Any]]: Extracted data or None if failed
        """
        response = self._make_request(url)
        if not response:
            return None
        
        soup = self._parse_html(response.text)
        
        # Initialize result dictionary with URL and timestamp
        result = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'status_code': response.status_code
        }
        
        # Extract text content
        if text_selectors:
            text_data = self._extract_text_content(soup, text_selectors)
            result.update(text_data)
        
        # Extract attributes
        if attr_selectors:
            attr_data = self._extract_attributes(soup, attr_selectors)
            result.update(attr_data)
        
        return result
    
    def scrape_multiple_pages(self, urls: List[str], text_selectors: Dict[str, str] = None,
                            attr_selectors: Dict[str, Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Scrape multiple pages and collect all data.
        
        Args:
            urls (List[str]): List of URLs to scrape
            text_selectors (Dict[str, str]): CSS selectors for text extraction
            attr_selectors (Dict[str, Dict[str, str]]): CSS selectors for attribute extraction
            
        Returns:
            List[Dict[str, Any]]: List of scraped data from all pages
        """
        self.logger.info(f"Starting to scrape {len(urls)} URLs")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Scraping page {i}/{len(urls)}: {url}")
            
            page_data = self.scrape_page(url, text_selectors, attr_selectors)
            if page_data:
                self.scraped_data.append(page_data)
        
        self.logger.info(f"Scraping completed. Success: {len(self.scraped_data)}, Failed: {len(self.failed_urls)}")
        return self.scraped_data
    
    def discover_links(self, base_url: str, link_pattern: str = None, 
                      max_pages: int = 100) -> List[str]:
        """
        Discover links from a base page using pattern matching.
        
        Args:
            base_url (str): Base URL to start discovery from
            link_pattern (str): Regex pattern to match links
            max_pages (int): Maximum number of links to discover
            
        Returns:
            List[str]: List of discovered URLs
        """
        response = self._make_request(base_url)
        if not response:
            return []
        
        soup = self._parse_html(response.text)
        links = []
        
        # Find all anchor tags
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Apply pattern matching if specified
            if link_pattern:
                if not re.search(link_pattern, full_url):
                    continue
            
            # Avoid duplicates
            if full_url not in links:
                links.append(full_url)
            
            # Respect max_pages limit
            if len(links) >= max_pages:
                break
        
        self.logger.info(f"Discovered {len(links)} links from {base_url}")
        return links
    
    def export_to_csv(self, filename: str = None) -> bool:
        """
        Export scraped data to CSV file.
        
        Args:
            filename (str): Output filename (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.scraped_data:
            self.logger.warning("No data to export")
            return False
        
        if not filename:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            # Get all unique keys from all records
            all_keys = set()
            for record in self.scraped_data:
                all_keys.update(record.keys())
            
            fieldnames = sorted(list(all_keys))
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in self.scraped_data:
                    # Handle list values by converting to string
                    processed_record = {}
                    for key, value in record.items():
                        if isinstance(value, list):
                            processed_record[key] = '; '.join(map(str, value))
                        else:
                            processed_record[key] = value
                    
                    writer.writerow(processed_record)
            
            self.logger.info(f"Data exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def export_to_json(self, filename: str = None) -> bool:
        """
        Export scraped data to JSON file.
        
        Args:
            filename (str): Output filename (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.scraped_data:
            self.logger.warning("No data to export")
            return False
        
        if not filename:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.scraped_data, jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get scraping statistics and summary.
        
        Returns:
            Dict[str, Any]: Statistics about the scraping session
        """
        return {
            'total_scraped': len(self.scraped_data),
            'failed_requests': len(self.failed_urls),
            'success_rate': len(self.scraped_data) / (len(self.scraped_data) + len(self.failed_urls)) * 100 if (len(self.scraped_data) + len(self.failed_urls)) > 0 else 0,
            'failed_urls': self.failed_urls
        }

# Example usage and demonstration
def example_usage():
    """
    Demonstrate the usage of WebScraper class with typical AI-generated examples.
    This function shows comprehensive usage patterns.
    """
    print("Web Scraper - AI Generated Example Usage")
    print("=" * 50)
    
    # Create configuration (example - not functional without real website)
    config = ScrapingConfig(
        base_url="https://example.com",
        headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
        delay_min=1.0,
        delay_max=2.0,
        timeout=30,
        max_retries=3
    )
    
    # Initialize scraper
    scraper = WebScraper(config)
    
    # Example selectors for text content
    text_selectors = {
        'title': 'h1',
        'description': '.description p',
        'tags': '.tags .tag'
    }
    
    # Example selectors for attributes
    attr_selectors = {
        'image_urls': {'selector': 'img', 'attribute': 'src'},
        'external_links': {'selector': 'a[href^="http"]', 'attribute': 'href'}
    }
    
    print("Configuration created successfully")
    print(f"Base URL: {config.base_url}")
    print(f"User Agent: {config.user_agent}")
    print("\nExample selectors configured:")
    print(f"Text selectors: {list(text_selectors.keys())}")
    print(f"Attribute selectors: {list(attr_selectors.keys())}")
    
    # Note: Actual scraping would require valid URLs
    # Example URLs for demonstration
    example_urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]
    
    print(f"\nWould scrape {len(example_urls)} URLs")
    print("Export options: CSV and JSON")
    print("\nThis is a demonstration - replace with actual URLs to use.")

if __name__ == "__main__":
    example_usage()