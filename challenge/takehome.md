# Augur Security - Sr Backend Take Home

### Pages

# Senior Backend Engineer - Take-Home Assignment

## Threat Intelligence API Development

### Overview

Build a set of REST API endpoints that power a threat intelligence dashboard. Security analysts use this system to investigate malicious indicators (IPs, domains, file hashes) and understand relationships between threats.

**Time Expectation:** 3-4 hours maximum

**Tech Stack:** Python (Flask/FastAPI) or Node.js (Express) - your choice

### What We're Providing

1. SQLite Database (`threat_intel.db`) with pre-populated data:
- 10,000 threat indicators (IPs, domains, URLs, file hashes)
- 50 threat actors
- 100 campaigns
- Relationships between indicators, campaigns, and threat actors
- Observation timestamps (when indicators were seen)
1. Database Schema (see `schema.sql`)
2. Basic Project Scaffold (optional - you can start from scratch if preferred)

### Your Task: Build 4 API Endpoints

**1. GET `/api/indicators/{id}`**

**Purpose:** Retrieve detailed information about a specific indicator

**Response should include:**

- Indicator details (type, value, confidence score)
- Associated threat actor(s) with confidence levels
- Associated campaign(s)
- First seen / Last seen timestamps
- Related indicators (limit to 5 most recent)

**Example Response:**

{ "id": "550e8400-e29b-41d4-a716-446655440000", "type": "ip", "value": "192.168.1.100", "confidence": 85, "first_seen": "2024-11-15T10:30:00Z", "last_seen": "2024-12-20T14:22:00Z", "threat_actors": [ { "id": "actor-123", "name": "APT-North", "confidence": 90 } ], "campaigns": [ { "id": "camp-456", "name": "Operation ShadowNet", "active": true } ], "related_indicators": [ { "id": "uuid", "type": "domain", "value": "malicious.example.com", "relationship": "same_campaign" } ] }

**2. GET `/api/indicators/search`**

**Purpose:** Search and filter indicators

**Query Parameters:**

- `type` - Filter by indicator type (ip, domain, url, hash)
- `value` - Partial match search on indicator value
- `threat_actor` - Filter by threat actor ID
- `campaign` - Filter by campaign ID
- `first_seen_after` - ISO date filter
- `last_seen_before` - ISO date filter
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20, max: 100)

**Response should include:**

- Array of matching indicators
- Total count of results
- Pagination metadata

**Example Response:**

{ "data": [ { "id": "uuid", "type": "domain", "value": "phishing.example.com", "confidence": 75, "first_seen": "2024-10-01T08:00:00Z", "campaign_count": 2, "threat_actor_count": 1 } ], "total": 156, "page": 1, "limit": 20, "total_pages": 8 }

**3. GET `/api/campaigns/{id}/indicators`**

**Purpose:** Get all indicators associated with a campaign, organized for timeline visualization

**Query Parameters:**

- `group_by` - Group results by "day" or "week" (default: "day")
- `start_date` - Optional filter
- `end_date` - Optional filter

**Response should include:**

- Campaign metadata
- Indicators grouped by time period
- Counts by indicator type per period
- Overall statistics

**Example Response:**

{ "campaign": { "id": "camp-456", "name": "Operation ShadowNet", "description": "Targeted phishing campaign", "first_seen": "2024-10-01T00:00:00Z", "last_seen": "2024-12-15T00:00:00Z", "status": "active" }, "timeline": [ { "period": "2024-10-01", "indicators": [ { "id": "uuid", "type": "ip", "value": "10.0.0.1" } ], "counts": { "ip": 5, "domain": 3, "url": 12 } } ], "summary": { "total_indicators": 234, "unique_ips": 45, "unique_domains": 67, "duration_days": 75 } }

**4. GET `/api/dashboard/summary`**

**Purpose:** Provide high-level statistics for the dashboard overview

**Query Parameters:**

- `time_range` - "24h", "7d", or "30d" (default: "7d")

**Response should include:**

- New indicators by type in time range
- Active campaigns count
- Most active threat actors (top 5)
- Indicator type distribution

**Example Response:**

{ "time_range": "7d", "new_indicators": { "ip": 145, "domain": 89, "url": 234, "hash": 67 }, "active_campaigns": 12, "top_threat_actors": [ { "id": "actor-123", "name": "APT-North", "indicator_count": 456 } ], "indicator_distribution": { "ip": 3421, "domain": 2876, "url": 2134, "hash": 1569 } }

### Technical Requirements

**Must Have:**

- Proper HTTP status codes (200, 404, 400, 500)
- Input validation with clear error messages
- Efficient database queries (avoid N+1 problems)
- Working pagination for search endpoint
- Basic error handling

**Nice to Have:**

- API documentation (Swagger/OpenAPI)
- Request rate limiting
- Caching strategy
- Unit tests for core logic
- Docker setup for easy running

**Don't Spend Time On:**

- Authentication/authorization (assume it's handled upstream)
- Complex frontend - API only
- Production deployment configuration
- Extensive logging/monitoring

### Deliverables

Please provide:

1. Source Code - Well-organized and commented
2. README.md with:
- Setup instructions (how to install dependencies and run)
- API documentation (or link to Swagger)
- Any assumptions you made
- What you'd improve with more time
1. Database Query Examples - Show at least 2 of your SQL queries with brief explanation of optimization approach
2. Brief Architecture Notes - How you structured the code and why

**Submission:** ZIP file or GitHub repository link

### Evaluation Criteria

We'll assess:

1. API Design (30%)
- Response structure suitable for frontend consumption
- Proper use of HTTP methods and status codes
- Sensible parameter naming and validation
1. Data Modeling & Queries (30%)
- Efficient SQL queries
- Proper joins and aggregations
- Handling of relationships between entities
1. Code Quality (25%)
- Clean, readable code structure
- Proper error handling
- Separation of concerns
1. Documentation (15%)
- Clear setup instructions
- API endpoint documentation
- Explanation of design decisions

### Review Discussion Topics

During the follow-up interview, we'll discuss:

- How would you scale this to handle 100M indicators?
- What caching strategy would you implement?
- How would you handle real-time threat feed ingestion?
- Security considerations for this API
- Performance optimization approaches

### Questions?

If anything is unclear or you encounter issues with the provided data, please email us. We want you to spend time showing your skills, not debugging our setup.

**Good luck! We're excited to see your approach.**

