#!/usr/bin/env python3
"""
Email Automation System - AI Generated Code
This module provides comprehensive email automation capabilities including
template management, bulk sending, and delivery tracking.
Author: AI Assistant
Created: Auto-generated
Version: 1.0.0
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
from dataclasses import dataclass, field
from jinja2 import Template, Environment, FileSystemLoader
import schedule
import threading
from pathlib import Path
import sqlite3

# Configure comprehensive logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_automation.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class EmailConfig:
    """
    Configuration class for email server settings.
    This dataclass encapsulates all SMTP configuration parameters.
    """
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    sender_name: str = "Email Automation System"
    sender_email: str = ""
    
    def __post_init__(self):
        """Post-initialization to set default sender email if not provided."""
        if not self.sender_email:
            self.sender_email = self.username

@dataclass
class EmailTemplate:
    """
    Data class for email templates with Jinja2 support.
    Supports both HTML and plain text templates with variable substitution.
    """
    name: str
    subject: str
    html_content: str = ""
    text_content: str = ""
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def render(self, context: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Render the template with provided context variables.
        
        Args:
            context (Dict[str, Any]): Variables to substitute in template
            
        Returns:
            Tuple[str, str, str]: Rendered (subject, html_content, text_content)
        """
        env = Environment()
        
        # Render subject
        subject_template = env.from_string(self.subject)
        rendered_subject = subject_template.render(**context)
        
        # Render HTML content
        rendered_html = ""
        if self.html_content:
            html_template = env.from_string(self.html_content)
            rendered_html = html_template.render(**context)
        
        # Render text content
        rendered_text = ""
        if self.text_content:
            text_template = env.from_string(self.text_content)
            rendered_text = text_template.render(**context)
        
        return rendered_subject, rendered_html, rendered_text

@dataclass
class EmailRecipient:
    """
    Data class representing an email recipient with personalization data.
    """
    email: str
    name: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed, bounced
    error_message: str = ""

class EmailTracker:
    """
    Database-backed email tracking system for delivery monitoring.
    Provides comprehensive tracking of email campaigns and delivery status.
    """
    
    def __init__(self, db_path: str = "email_tracking.db"):
        """
        Initialize the email tracker with SQLite database.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create campaigns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS campaigns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        template_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_recipients INTEGER DEFAULT 0,
                        sent_count INTEGER DEFAULT 0,
                        failed_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'active'
                    )
                ''')
                
                # Create email_logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_id INTEGER,
                        recipient_email TEXT NOT NULL,
                        recipient_name TEXT,
                        subject TEXT,
                        sent_at TIMESTAMP,
                        status TEXT DEFAULT 'pending',
                        error_message TEXT,
                        FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {str(e)}")
    
    def create_campaign(self, name: str, template_name: str, recipients: List[EmailRecipient]) -> int:
        """
        Create a new email campaign in the database.
        
        Args:
            name (str): Campaign name
            template_name (str): Template identifier
            recipients (List[EmailRecipient]): List of recipients
            
        Returns:
            int: Campaign ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create campaign record
                cursor.execute('''
                    INSERT INTO campaigns (name, template_name, total_recipients)
                    VALUES (?, ?, ?)
                ''', (name, template_name, len(recipients)))
                
                campaign_id = cursor.lastrowid
                
                # Add recipient records
                for recipient in recipients:
                    cursor.execute('''
                        INSERT INTO email_logs (campaign_id, recipient_email, recipient_name, status)
                        VALUES (?, ?, ?, ?)
                    ''', (campaign_id, recipient.email, recipient.name, recipient.status))
                
                conn.commit()
                self.logger.info(f"Campaign '{name}' created with ID {campaign_id}")
                return campaign_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Error creating campaign: {str(e)}")
            return -1
    
    def update_email_status(self, campaign_id: int, recipient_email: str, 
                           status: str, error_message: str = "") -> None:
        """
        Update the delivery status of a specific email.
        
        Args:
            campaign_id (int): Campaign identifier
            recipient_email (str): Recipient's email address
            status (str): New status (sent, failed, bounced)
            error_message (str): Error message if applicable
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE email_logs 
                    SET status = ?, sent_at = CURRENT_TIMESTAMP, error_message = ?
                    WHERE campaign_id = ? AND recipient_email = ?
                ''', (status, error_message, campaign_id, recipient_email))
                
                # Update campaign statistics
                if status == 'sent':
                    cursor.execute('''
                        UPDATE campaigns 
                        SET sent_count = sent_count + 1
                        WHERE id = ?
                    ''', (campaign_id,))
                elif status == 'failed':
                    cursor.execute('''
                        UPDATE campaigns 
                        SET failed_count = failed_count + 1
                        WHERE id = ?
                    ''', (campaign_id,))
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating email status: {str(e)}")
    
    def get_campaign_statistics(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a campaign.
        
        Args:
            campaign_id (int): Campaign identifier
            
        Returns:
            Dict[str, Any]: Campaign statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get campaign info
                cursor.execute('''
                    SELECT * FROM campaigns WHERE id = ?
                ''', (campaign_id,))
                
                campaign_data = cursor.fetchone()
                if not campaign_data:
                    return {}
                
                # Get detailed statistics
                cursor.execute('''
                    SELECT status, COUNT(*) as count
                    FROM email_logs 
                    WHERE campaign_id = ?
                    GROUP BY status
                ''', (campaign_id,))
                
                status_counts = dict(cursor.fetchall())
                
                return {
                    'campaign_id': campaign_id,
                    'name': campaign_data[1],
                    'template_name': campaign_data[2],
                    'created_at': campaign_data[3],
                    'total_recipients': campaign_data[4],
                    'sent_count': campaign_data[5],
                    'failed_count': campaign_data[6],
                    'status_breakdown': status_counts,
                    'success_rate': (campaign_data[5] / campaign_data[4] * 100) if campaign_data[4] > 0 else 0
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting campaign statistics: {str(e)}")
            return {}

class EmailAutomationSystem:
    """
    Comprehensive email automation system with template management,
    bulk sending capabilities, and delivery tracking.
    
    This class provides a complete solution for email marketing and
    automated communication needs.
    """
    
    def __init__(self, config: EmailConfig):
        """
        Initialize the email automation system.
        
        Args:
            config (EmailConfig): Email server configuration
        """
        self.config = config
        self.templates: Dict[str, EmailTemplate] = {}
        self.tracker = EmailTracker()
        self.logger = logging.getLogger(__name__)
        
        # Initialize SMTP connection pool
        self._smtp_connection = None
        self._connection_lock = threading.Lock()
        
        self.logger.info("Email Automation System initialized")
    
    def _get_smtp_connection(self) -> smtplib.SMTP:
        """
        Get or create SMTP connection with proper error handling.
        
        Returns:
            smtplib.SMTP: SMTP connection object
        """
        with self._connection_lock:
            if self._smtp_connection is None:
                try:
                    if self.config.use_ssl:
                        context = ssl.create_default_context()
                        self._smtp_connection = smtplib.SMTP_SSL(
                            self.config.smtp_server, 
                            self.config.smtp_port, 
                            context=context
                        )
                    else:
                        self._smtp_connection = smtplib.SMTP(
                            self.config.smtp_server, 
                            self.config.smtp_port
                        )
                        
                        if self.config.use_tls:
                            self._smtp_connection.starttls()
                    
                    # Login to server
                    self._smtp_connection.login(self.config.username, self.config.password)
                    self.logger.info("SMTP connection established successfully")
                    
                except Exception as e:
                    self.logger.error(f"Failed to establish SMTP connection: {str(e)}")
                    raise
            
            return self._smtp_connection
    
    def add_template(self, template: EmailTemplate) -> None:
        """
        Add an email template to the system.
        
        Args:
            template (EmailTemplate): Template to add
        """
        self.templates[template.name] = template
        self.logger.info(f"Template '{template.name}' added successfully")
    
    def load_template_from_file(self, name: str, template_dir: str = "templates") -> bool:
        """
        Load email template from file system.
        
        Args:
            name (str): Template name
            template_dir (str): Directory containing template files
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            template_path = Path(template_dir) / name
            
            # Load template configuration
            config_file = template_path / "config.json"
            if not config_file.exists():
                self.logger.error(f"Template config not found: {config_file}")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load HTML template
            html_file = template_path / "template.html"
            html_content = ""
            if html_file.exists():
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            
            # Load text template
            text_file = template_path / "template.txt"
            text_content = ""
            if text_file.exists():
                with open(text_file, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            
            # Create template object
            template = EmailTemplate(
                name=name,
                subject=config_data.get('subject', ''),
                html_content=html_content,
                text_content=text_content,
                variables=config_data.get('variables', [])
            )
            
            self.add_template(template)
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading template from file: {str(e)}")
            return False
    
    def send_single_email(self, recipient: EmailRecipient, template_name: str, 
                         attachments: List[str] = None) -> bool:
        """
        Send a single email using specified template.
        
        Args:
            recipient (EmailRecipient): Email recipient
            template_name (str): Name of template to use
            attachments (List[str]): List of file paths to attach
            
        Returns:
            bool: True if successful, False otherwise
        """
        if template_name not in self.templates:
            self.logger.error(f"Template '{template_name}' not found")
            return False
        
        template = self.templates[template_name]
        
        try:
            # Render template with recipient variables
            context = {
                'name': recipient.name,
                'email': recipient.email,
                **recipient.variables
            }
            
            subject, html_content, text_content = template.render(context)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg['To'] = recipient.email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            smtp_conn = self._get_smtp_connection()
            smtp_conn.send_message(msg)
            
            # Update recipient status
            recipient.sent_at = datetime.now()
            recipient.status = "sent"
            
            self.logger.info(f"Email sent successfully to {recipient.email}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            recipient.status = "failed"
            recipient.error_message = error_msg
            self.logger.error(f"Failed to send email to {recipient.email}: {error_msg}")
            return False
    
    def send_bulk_emails(self, recipients: List[EmailRecipient], template_name: str,
                        campaign_name: str = "", delay_between_emails: float = 1.0,
                        batch_size: int = 50) -> Dict[str, Any]:
        """
        Send bulk emails with rate limiting and progress tracking.
        
        Args:
            recipients (List[EmailRecipient]): List of email recipients
            template_name (str): Template to use for emails
            campaign_name (str): Name for the campaign
            delay_between_emails (float): Delay between sends in seconds
            batch_size (int): Number of emails per batch
            
        Returns:
            Dict[str, Any]: Campaign results and statistics
        """
        if not campaign_name:
            campaign_name = f"Campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create campaign in database
        campaign_id = self.tracker.create_campaign(campaign_name, template_name, recipients)
        
        sent_count = 0
        failed_count = 0
        
        self.logger.info(f"Starting bulk email campaign: {campaign_name}")
        self.logger.info(f"Recipients: {len(recipients)}, Batch size: {batch_size}")
        
        # Process recipients in batches
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            self.logger.info(f"Processing batch {i // batch_size + 1}")
            
            for recipient in batch:
                # Send individual email
                success = self.send_single_email(recipient, template_name)
                
                # Update tracking
                if success:
                    sent_count += 1
                    self.tracker.update_email_status(campaign_id, recipient.email, "sent")
                else:
                    failed_count += 1
                    self.tracker.update_email_status(
                        campaign_id, recipient.email, "failed", recipient.error_message
                    )
                
                # Rate limiting
                if delay_between_emails > 0:
                    time.sleep(delay_between_emails)
            
            # Brief pause between batches
            time.sleep(2.0)
        
        # Generate final results
        results = {
            'campaign_id': campaign_id,
            'campaign_name': campaign_name,
            'template_name': template_name,
            'total_recipients': len(recipients),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'success_rate': (sent_count / len(recipients)) * 100 if recipients else 0,
            'completed_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Bulk email campaign completed: {sent_count} sent, {failed_count} failed")
        return results
    
    def load_recipients_from_csv(self, file_path: str) -> List[EmailRecipient]:
        """
        Load email recipients from CSV file.
        
        Args:
            file_path (str): Path to CSV file
            
        Returns:
            List[EmailRecipient]: List of loaded recipients
        """
        recipients = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                delimiter = ',' if ',' in sample else ';'
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row in reader:
                    # Extract required fields
                    email = row.get('email', '').strip()
                    if not email:
                        continue
                    
                    name = row.get('name', '').strip()
                    
                    # Extract additional variables (all other columns)
                    variables = {}
                    for key, value in row.items():
                        if key not in ['email', 'name']:
                            variables[key] = value
                    
                    recipient = EmailRecipient(
                        email=email,
                        name=name,
                        variables=variables
                    )
                    
                    recipients.append(recipient)
            
            self.logger.info(f"Loaded {len(recipients)} recipients from {file_path}")
            return recipients
            
        except Exception as e:
            self.logger.error(f"Error loading recipients from CSV: {str(e)}")
            return []
    
    def schedule_campaign(self, recipients: List[EmailRecipient], template_name: str,
                         send_time: datetime, campaign_name: str = "") -> bool:
        """
        Schedule a bulk email campaign for future delivery.
        
        Args:
            recipients (List[EmailRecipient]): Recipients list
            template_name (str): Template to use
            send_time (datetime): When to send the campaign
            campaign_name (str): Campaign identifier
            
        Returns:
            bool: True if scheduled successfully
        """
        def send_scheduled_campaign():
            """Inner function to execute the scheduled campaign."""
            self.logger.info(f"Executing scheduled campaign: {campaign_name}")
            return self.send_bulk_emails(recipients, template_name, campaign_name)
        
        try:
            # Schedule the campaign
            schedule.every().day.at(send_time.strftime("%H:%M")).do(send_scheduled_campaign)
            
            self.logger.info(f"Campaign '{campaign_name}' scheduled for {send_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling campaign: {str(e)}")
            return False
    
    def close_connection(self) -> None:
        """Close SMTP connection and cleanup resources."""
        with self._connection_lock:
            if self._smtp_connection:
                try:
                    self._smtp_connection.quit()
                    self.logger.info("SMTP connection closed")
                except:
                    pass
                finally:
                    self._smtp_connection = None

# Example usage and demonstration
def example_usage():
    """
    Comprehensive example demonstrating all features of the email automation system.
    This example shows typical AI-generated usage patterns with detailed comments.
    """
    print("Email Automation System - AI Generated Example")
    print("=" * 55)
    
    # Example configuration (replace with actual credentials)
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your_email@gmail.com",
        password="your_app_password",
        use_tls=True,
        sender_name="Your Organization",
        sender_email="your_email@gmail.com"
    )
    
    # Initialize the system
    email_system = EmailAutomationSystem(config)
    
    # Create a sample template
    template = EmailTemplate(
        name="welcome_email",
        subject="Welcome to Our Service, {{ name }}!",
        html_content="""
        <html>
            <body>
                <h2>Welcome {{ name }}!</h2>
                <p>Thank you for joining our service. We're excited to have you aboard.</p>
                <p>Your account email: {{ email }}</p>
                <p>Best regards,<br>The Team</p>
            </body>
        </html>
        """,
        text_content="""
        Welcome {{ name }}!
        
        Thank you for joining our service. We're excited to have you aboard.
        Your account email: {{ email }}
        
        Best regards,
        The Team
        """,
        variables=["name", "email"]
    )
    
    email_system.add_template(template)
    
    # Create sample recipients
    recipients = [
        EmailRecipient(
            email="user1@example.com",
            name="John Doe",
            variables={"signup_date": "2024-01-15"}
        ),
        EmailRecipient(
            email="user2@example.com", 
            name="Jane Smith",
            variables={"signup_date": "2024-01-16"}
        )
    ]
    
    print("System initialized successfully!")
    print(f"Template '{template.name}' created with {len(template.variables)} variables")
    print(f"Loaded {len(recipients)} sample recipients")
    print("\nTo use this system:")
    print("1. Update the EmailConfig with your actual SMTP credentials")
    print("2. Replace sample recipients with real email addresses")
    print("3. Call email_system.send_bulk_emails() to send campaign")
    print("4. Use email_system.tracker.get_campaign_statistics() for tracking")

if __name__ == "__main__":
    example_usage()