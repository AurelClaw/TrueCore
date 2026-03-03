#!/usr/bin/env python3
"""
KNOWLEDGE ARCHAEOLOGY LOOP

Autonomous research system for discovering hidden ancient knowledge.

Capabilities:
1. Discovery - Find obscure/forgotten knowledge
2. Cartography - Map knowledge domains
3. Analysis - Deep understanding
4. Connection - Link to modern concepts
5. Synthesis - Find parallels across time

Uses web search to dig through layers of time.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import hashlib

class KnowledgeArchaeology:
    """
    Main research loop for ancient knowledge discovery.
    
    Metaphor: Archaeological dig through knowledge layers
    - Surface layer: Common knowledge (Wikipedia, textbooks)
    - Middle layer: Academic papers, specialized books
    - Deep layer: Obscure texts, untranslated works, oral traditions
    - Bedrock: Lost knowledge (reconstructed from fragments)
    """
    
    def __init__(self, research_dir: str = "/RESEARCH"):
        self.research_dir = Path(research_dir)
        self.research_dir.mkdir(exist_ok=True)
        
        # Initialize knowledge graph
        self.knowledge_graph = {
            'nodes': {},  # Concepts/entities
            'edges': {},  # Relationships
            'layers': {  # Time layers
                'ancient': {},      # Before 500 CE
                'medieval': {},     # 500-1500 CE
                'early_modern': {}, # 1500-1800 CE
                'modern': {},       # 1800-1950 CE
                'contemporary': {}  # 1950-today
            },
            'domains': {  # Knowledge domains
                'philosophy': {},
                'science': {},
                'mysticism': {},
                'technology': {},
                'arts': {},
                'medicine': {}
            }
        }
        
        # Research state
        self.discoveries = []
        self.connections = []
        self.parallels = []
        self.research_questions = []
        
        # Seen URLs (avoid duplicates)
        self.seen_urls = set()
        
        # Log
        self.log_file = self.research_dir / "archaeology.log"
    
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] {message}\n"
        print(entry.strip())
        
        with open(self.log_file, 'a') as f:
            f.write(entry)
    
    def research_cycle(self, seed_topic: str, depth: int = 3):
        """
        One complete research cycle.
        
        Phases:
        1. DISCOVERY - Find sources
        2. EXCAVATION - Extract knowledge
        3. CARTOGRAPHY - Map relationships
        4. ANALYSIS - Deep understanding
        5. SYNTHESIS - Modern connections
        6. PUBLICATION - Document findings
        """
        
        self.log(f"{'='*60}")
        self.log(f"RESEARCH CYCLE: {seed_topic}")
        self.log(f"{'='*60}")
        
        # Phase 1: DISCOVERY
        self.log("PHASE 1: DISCOVERY - Finding sources...")
        sources = self.discover_sources(seed_topic, depth)
        self.log(f"Discovered {len(sources)} sources")
        
        # Phase 2: EXCAVATION
        self.log("PHASE 2: EXCAVATION - Extracting knowledge...")
        knowledge_fragments = self.excavate_knowledge(sources)
        self.log(f"Excavated {len(knowledge_fragments)} knowledge fragments")
        
        # Phase 3: CARTOGRAPHY
        self.log("PHASE 3: CARTOGRAPHY - Mapping relationships...")
        self.map_knowledge(knowledge_fragments)
        self.log(f"Mapped {len(self.knowledge_graph['nodes'])} nodes")
        
        # Phase 4: ANALYSIS
        self.log("PHASE 4: ANALYSIS - Deep analysis...")
        insights = self.analyze_knowledge(knowledge_fragments)
        self.log(f"Generated {len(insights)} insights")
        
        # Phase 5: SYNTHESIS
        self.log("PHASE 5: SYNTHESIS - Finding modern connections...")
        self.find_modern_parallels(knowledge_fragments)
        self.log(f"Found {len(self.parallels)} parallels")
        
        # Phase 6: PUBLICATION
        self.log("PHASE 6: PUBLICATION - Documenting findings...")
        report = self.generate_report(seed_topic)
        self.save_report(report, seed_topic)
        
        return report
    
    def discover_sources(self, topic: str, depth: int = 3) -> List[Dict]:
        """
        PHASE 1: DISCOVERY
        
        Find sources about ancient knowledge on topic.
        Uses progressive deepening:
        - Level 1: Surface web (Wikipedia, general sites)
        - Level 2: Academic sources (papers, books)
        - Level 3: Obscure sources (archives, translations)
        """
        
        sources = []
        
        # Level 1: Surface search
        surface_queries = [
            f"{topic} ancient history",
            f"{topic} historical origins",
            f"history of {topic}"
        ]
        
        for query in surface_queries:
            results = self.web_search(query, max_results=5)
            sources.extend(self.process_search_results(results, layer='surface'))
        
        if depth < 2:
            return sources
        
        # Level 2: Academic search
        academic_queries = [
            f"{topic} historical development scholarly",
            f"{topic} ancient texts primary sources",
            f"etymology origin {topic}"
        ]
        
        for query in academic_queries:
            results = self.web_search(query, max_results=5)
            sources.extend(self.process_search_results(results, layer='academic'))
        
        if depth < 3:
            return sources
        
        # Level 3: Deep search
        deep_queries = [
            f"{topic} forgotten knowledge lost traditions",
            f"{topic} esoteric hermetic ancient wisdom",
            f"{topic} untranslated manuscripts rare texts"
        ]
        
        for query in deep_queries:
            results = self.web_search(query, max_results=3)
            sources.extend(self.process_search_results(results, layer='deep'))
        
        return sources
    
    def web_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform web search.
        
        NOTE: In real implementation, this would use the web_search tool.
        For now, returns placeholder structure.
        """
        
        self.log(f"  Searching: {query}")
        
        # TODO: Replace with actual web_search tool call
        # For now, return placeholder
        return [
            {
                'title': f"Result for: {query}",
                'url': f"https://example.com/{hashlib.md5(query.encode()).hexdigest()}",
                'snippet': f"Information about {query}...",
                'source_type': 'web'
            }
        ]
    
    def process_search_results(
        self,
        results: List[Dict],
        layer: str
    ) -> List[Dict]:
        """Process search results into source objects"""
        
        sources = []
        
        for result in results:
            url = result.get('url', '')
            
            # Skip if already seen
            if url in self.seen_urls:
                continue
            
            self.seen_urls.add(url)
            
            source = {
                'url': url,
                'title': result.get('title', ''),
                'snippet': result.get('snippet', ''),
                'layer': layer,
                'discovered_at': datetime.now().isoformat(),
                'credibility': self.assess_credibility(result),
                'time_period': self.infer_time_period(result),
                'domain': self.classify_domain(result)
            }
            
            sources.append(source)
        
        return sources
    
    def assess_credibility(self, result: Dict) -> float:
        """
        Assess source credibility (0-1).
        
        Factors:
        - Domain authority (.edu, .org, known archives)
        - Presence of citations
        - Academic language
        - Primary vs secondary source
        """
        
        url = result.get('url', '')
        snippet = result.get('snippet', '')
        
        credibility = 0.5  # Base
        
        # Domain bonuses
        if '.edu' in url or '.ac.' in url:
            credibility += 0.2
        if 'archive.org' in url or 'jstor' in url or 'scholar.google' in url:
            credibility += 0.2
        if 'wikipedia' in url:
            credibility += 0.1
        
        # Content signals
        if any(word in snippet.lower() for word in ['scholar', 'research', 'study', 'journal']):
            credibility += 0.1
        if any(word in snippet.lower() for word in ['primary source', 'manuscript', 'original text']):
            credibility += 0.2
        
        return min(credibility, 1.0)
    
    def infer_time_period(self, result: Dict) -> str:
        """Infer historical time period from source"""
        
        snippet = result.get('snippet', '').lower()
        title = result.get('title', '').lower()
        text = snippet + " " + title
        
        # Time period keywords
        if any(word in text for word in ['ancient', 'antiquity', 'classical', 'bc', 'bce']):
            return 'ancient'
        if any(word in text for word in ['medieval', 'middle ages', 'byzantine']):
            return 'medieval'
        if any(word in text for word in ['renaissance', 'enlightenment', '16th', '17th', '18th']):
            return 'early_modern'
        if any(word in text for word in ['19th', '20th', 'industrial', 'victorian']):
            return 'modern'
        
        return 'contemporary'
    
    def classify_domain(self, result: Dict) -> str:
        """Classify knowledge domain"""
        
        text = (result.get('snippet', '') + " " + result.get('title', '')).lower()
        
        # Domain keywords
        domains = {
            'philosophy': ['philosophy', 'metaphysics', 'epistemology', 'ontology'],
            'science': ['science', 'mathematics', 'astronomy', 'physics', 'chemistry'],
            'mysticism': ['mysticism', 'esoteric', 'hermetic', 'alchemy', 'occult'],
            'technology': ['technology', 'invention', 'engineering', 'craft'],
            'arts': ['art', 'music', 'literature', 'poetry', 'architecture'],
            'medicine': ['medicine', 'healing', 'health', 'anatomy', 'surgery']
        }
        
        scores = {}
        for domain, keywords in domains.items():
            scores[domain] = sum(1 for kw in keywords if kw in text)
        
        if max(scores.values()) == 0:
            return 'general'
        
        return max(scores, key=scores.get)
    
    def excavate_knowledge(self, sources: List[Dict]) -> List[Dict]:
        """
        PHASE 2: EXCAVATION
        
        Extract knowledge fragments from sources.
        Each fragment is a piece of ancient knowledge.
        """
        
        fragments = []
        
        for source in sources:
            # In real implementation, would fetch and parse URL
            # For now, extract from snippet
            
            fragment = {
                'id': self.generate_fragment_id(source),
                'source': source['url'],
                'content': source['snippet'],
                'layer': source['layer'],
                'time_period': source['time_period'],
                'domain': source['domain'],
                'credibility': source['credibility'],
                'extracted_at': datetime.now().isoformat(),
                'concepts': self.extract_concepts(source['snippet']),
                'entities': self.extract_entities(source['snippet']),
                'relationships': []
            }
            
            fragments.append(fragment)
        
        return fragments
    
    def generate_fragment_id(self, source: Dict) -> str:
        """Generate unique ID for knowledge fragment"""
        unique = f"{source['url']}_{source['discovered_at']}"
        return hashlib.md5(unique.encode()).hexdigest()[:12]
    
    def extract_concepts(self, text: str) -> List[str]:
        """
        Extract key concepts from text.
        
        Uses simple NLP heuristics:
        - Capitalized words (entities)
        - Technical terms
        - Repeated words
        """
        
        # Simple extraction (in real implementation, use proper NLP)
        words = text.split()
        
        concepts = []
        
        # Capitalized words
        for word in words:
            if word[0].isupper() and len(word) > 3:
                concepts.append(word.strip('.,;:!?()[]'))
        
        # Remove duplicates, keep order
        seen = set()
        unique_concepts = []
        for c in concepts:
            if c.lower() not in seen:
                seen.add(c.lower())
                unique_concepts.append(c)
        
        return unique_concepts[:10]  # Top 10
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities.
        
        Categories:
        - People
        - Places
        - Dates
        - Works (books, texts)
        """
        
        # Placeholder (real implementation would use NER)
        return {
            'people': [],
            'places': [],
            'dates': [],
            'works': []
        }
    
    def map_knowledge(self, fragments: List[Dict]):
        """
        PHASE 3: CARTOGRAPHY
        
        Build knowledge graph from fragments.
        Creates nodes and edges.
        """
        
        for fragment in fragments:
            
            # Add fragment as node
            node_id = fragment['id']
            
            self.knowledge_graph['nodes'][node_id] = {
                'type': 'fragment',
                'content': fragment['content'][:200],  # Truncate
                'time_period': fragment['time_period'],
                'domain': fragment['domain'],
                'credibility': fragment['credibility'],
                'concepts': fragment['concepts']
            }
            
            # Add to appropriate layer
            layer = self.knowledge_graph['layers'][fragment['time_period']]
            layer[node_id] = self.knowledge_graph['nodes'][node_id]
            
            # Add to domain
            domain = self.knowledge_graph['domains'][fragment['domain']]
            domain[node_id] = self.knowledge_graph['nodes'][node_id]
            
            # Create edges (connections between concepts)
            for concept in fragment['concepts']:
                concept_id = f"concept_{concept.lower()}"
                
                if concept_id not in self.knowledge_graph['nodes']:
                    self.knowledge_graph['nodes'][concept_id] = {
                        'type': 'concept',
                        'name': concept,
                        'appearances': []
                    }
                
                # Link fragment to concept
                edge_id = f"{node_id}_{concept_id}"
                self.knowledge_graph['edges'][edge_id] = {
                    'from': node_id,
                    'to': concept_id,
                    'type': 'contains_concept'
                }
                
                # Track concept appearances
                self.knowledge_graph['nodes'][concept_id]['appearances'].append({
                    'fragment': node_id,
                    'time_period': fragment['time_period']
                })
    
    def analyze_knowledge(self, fragments: List[Dict]) -> List[Dict]:
        """
        PHASE 4: ANALYSIS
        
        Deep analysis of knowledge fragments.
        Generates insights about:
        - Patterns across time
        - Evolution of concepts
        - Lost knowledge
        - Transmission chains
        """
        
        insights = []
        
        # Insight 1: Concept evolution
        concept_evolution = self.trace_concept_evolution()
        insights.extend(concept_evolution)
        
        # Insight 2: Knowledge clusters
        clusters = self.find_knowledge_clusters()
        insights.extend(clusters)
        
        # Insight 3: Transmission chains
        chains = self.identify_transmission_chains()
        insights.extend(chains)
        
        # Insight 4: Lost knowledge
        lost = self.identify_lost_knowledge()
        insights.extend(lost)
        
        return insights
    
    def trace_concept_evolution(self) -> List[Dict]:
        """Trace how concepts evolved over time"""
        
        evolutions = []
        
        # Find concepts that appear in multiple time periods
        for node_id, node in self.knowledge_graph['nodes'].items():
            if node['type'] != 'concept':
                continue
            
            if len(node.get('appearances', [])) < 2:
                continue
            
            # Trace through time
            timeline = {}
            for appearance in node['appearances']:
                period = appearance['time_period']
                if period not in timeline:
                    timeline[period] = []
                timeline[period].append(appearance['fragment'])
            
            if len(timeline) > 1:
                evolutions.append({
                    'type': 'concept_evolution',
                    'concept': node['name'],
                    'timeline': timeline,
                    'insight': f"Concept '{node['name']}' appears across {len(timeline)} time periods"
                })
        
        return evolutions
    
    def find_knowledge_clusters(self) -> List[Dict]:
        """Find clusters of related knowledge"""
        
        clusters = []
        
        # Group by domain and time period
        for domain_name, domain_nodes in self.knowledge_graph['domains'].items():
            if len(domain_nodes) < 3:
                continue
            
            clusters.append({
                'type': 'domain_cluster',
                'domain': domain_name,
                'size': len(domain_nodes),
                'time_spread': self.calculate_time_spread(domain_nodes),
                'insight': f"Found {len(domain_nodes)} fragments in {domain_name} domain"
            })
        
        return clusters
    
    def calculate_time_spread(self, nodes: Dict) -> Dict:
        """Calculate distribution across time periods"""
        
        distribution = {}
        
        for node_id, node in nodes.items():
            period = node.get('time_period', 'unknown')
            distribution[period] = distribution.get(period, 0) + 1
        
        return distribution
    
    def identify_transmission_chains(self) -> List[Dict]:
        """Identify how knowledge was transmitted"""
        
        chains = []
        
        # Find concepts that appear sequentially through time
        time_order = ['ancient', 'medieval', 'early_modern', 'modern', 'contemporary']
        
        for node_id, node in self.knowledge_graph['nodes'].items():
            if node['type'] != 'concept':
                continue
            
            appearances = node.get('appearances', [])
            if len(appearances) < 2:
                continue
            
            # Check if appears in sequential periods
            periods = [a['time_period'] for a in appearances]
            period_indices = [time_order.index(p) for p in periods if p in time_order]
            
            if len(period_indices) >= 2:
                # Check for continuity
                if max(period_indices) - min(period_indices) == len(period_indices) - 1:
                    chains.append({
                        'type': 'transmission_chain',
                        'concept': node['name'],
                        'chain': [time_order[i] for i in sorted(period_indices)],
                        'insight': f"Concept '{node['name']}' shows continuous transmission"
                    })
        
        return chains
    
    def identify_lost_knowledge(self) -> List[Dict]:
        """Identify knowledge that appears then disappears"""
        
        lost = []
        
        time_order = ['ancient', 'medieval', 'early_modern', 'modern', 'contemporary']
        
        for node_id, node in self.knowledge_graph['nodes'].items():
            if node['type'] != 'concept':
                continue
            
            appearances = node.get('appearances', [])
            if len(appearances) < 1:
                continue
            
            periods = [a['time_period'] for a in appearances]
            period_indices = [time_order.index(p) for p in periods if p in time_order]
            
            if period_indices:
                # If last appearance is not contemporary, knowledge may be lost
                if max(period_indices) < len(time_order) - 1:
                    last_period = time_order[max(period_indices)]
                    
                    lost.append({
                        'type': 'lost_knowledge',
                        'concept': node['name'],
                        'last_seen': last_period,
                        'insight': f"Concept '{node['name']}' last documented in {last_period} period"
                    })
        
        return lost
    
    def find_modern_parallels(self, fragments: List[Dict]):
        """
        PHASE 5: SYNTHESIS
        
        Find parallels between ancient knowledge and modern concepts.
        """
        
        self.log("  Searching for modern parallels...")
        
        # For each ancient concept, search for modern equivalents
        ancient_concepts = []
        
        for node_id, node in self.knowledge_graph['nodes'].items():
            if node['type'] != 'concept':
                continue
            
            # Check if concept is from ancient/medieval period
            appearances = node.get('appearances', [])
            if not appearances:
                continue
            
            periods = [a['time_period'] for a in appearances]
            if 'ancient' in periods or 'medieval' in periods:
                ancient_concepts.append(node['name'])
        
        # Search for modern connections
        for concept in ancient_concepts[:10]:  # Limit to avoid too many searches
            
            # Search for modern interpretations
            modern_query = f"{concept} modern interpretation contemporary relevance"
            results = self.web_search(modern_query, max_results=3)
            
            for result in results:
                parallel = {
                    'ancient_concept': concept,
                    'modern_connection': result.get('title', ''),
                    'description': result.get('snippet', ''),
                    'url': result.get('url', ''),
                    'discovered_at': datetime.now().isoformat()
                }
                
                self.parallels.append(parallel)
                
                self.log(f"  Found parallel: {concept} → {result.get('title', '')}")
    
    def generate_report(self, seed_topic: str) -> str:
        """
        PHASE 6: PUBLICATION
        
        Generate comprehensive research report.
        """
        
        report = f"""# KNOWLEDGE ARCHAEOLOGY REPORT
## Topic: {seed_topic}

**Generated:** {datetime.now().isoformat()}

---

## EXECUTIVE SUMMARY

This research cycle explored ancient and hidden knowledge related to {seed_topic}.

**Metrics:**
- Sources discovered: {len(self.seen_urls)}
- Knowledge fragments: {len(self.knowledge_graph['nodes'])}
- Time periods covered: {len([p for p, nodes in self.knowledge_graph['layers'].items() if nodes])}
- Domains explored: {len([d for d, nodes in self.knowledge_graph['domains'].items() if nodes])}
- Modern parallels: {len(self.parallels)}

---

## KNOWLEDGE MAP

### Distribution Across Time

"""
        
        for period, nodes in self.knowledge_graph['layers'].items():
            if nodes:
                report += f"**{period.replace('_', ' ').title()}**: {len(nodes)} fragments\n"
        
        report += "\n### Distribution Across Domains\n\n"
        
        for domain, nodes in self.knowledge_graph['domains'].items():
            if nodes:
                report += f"**{domain.title()}**: {len(nodes)} fragments\n"
        
        report += "\n---\n\n## KEY DISCOVERIES\n\n"
        
        # List top concepts by appearance frequency
        concept_counts = {}
        for node_id, node in self.knowledge_graph['nodes'].items():
            if node['type'] == 'concept':
                concept_counts[node['name']] = len(node.get('appearances', []))
        
        top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for concept, count in top_concepts:
            report += f"- **{concept}**: appears in {count} fragments\n"
        
        report += "\n---\n\n## ANCIENT → MODERN PARALLELS\n\n"
        
        for parallel in self.parallels[:10]:  # Top 10
            report += f"""### {parallel['ancient_concept']}

**Modern Connection:** {parallel['modern_connection']}

{parallel['description']}

[Source]({parallel['url']})

---

"""
        
        report += "\n## KNOWLEDGE GRAPH STRUCTURE\n\n"
        report += f"Nodes: {len(self.knowledge_graph['nodes'])}\n"
        report += f"Edges: {len(self.knowledge_graph['edges'])}\n"
        
        report += "\n---\n\n## RESEARCH QUESTIONS FOR FUTURE\n\n"
        
        # Generate future research questions
        questions = self.generate_research_questions()
        
        for q in questions:
            report += f"- {q}\n"
        
        return report
    
    def generate_research_questions(self) -> List[str]:
        """Generate follow-up research questions"""
        
        questions = []
        
        # Questions about lost knowledge
        for node_id, node in self.knowledge_graph['nodes'].items():
            if node['type'] == 'concept':
                appearances = node.get('appearances', [])
                if appearances:
                    periods = [a['time_period'] for a in appearances]
                    if 'ancient' in periods and 'contemporary' not in periods:
                        questions.append(
                            f"What happened to the knowledge of {node['name']} "
                            f"after the {periods[-1]} period?"
                        )
        
        # Questions about transmission
        time_order = ['ancient', 'medieval', 'early_modern', 'modern', 'contemporary']
        
        for period in time_order:
            layer = self.knowledge_graph['layers'][period]
            if len(layer) > 3:
                questions.append(
                    f"What were the primary transmission mechanisms "
                    f"of knowledge during the {period} period?"
                )
        
        # Questions about domains
        for domain, nodes in self.knowledge_graph['domains'].items():
            if len(nodes) > 5:
                questions.append(
                    f"How did {domain} knowledge interact with other domains "
                    f"in ancient times?"
                )
        
        return questions[:10]  # Top 10
    
    def save_report(self, report: str, topic: str):
        """Save report to file"""
        
        # Clean topic for filename
        clean_topic = topic.replace(' ', '_').replace('/', '_')[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"research_{clean_topic}_{timestamp}.md"
        filepath = self.research_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        self.log(f"Report saved: {filepath}")
        
        # Also save knowledge graph as JSON
        graph_file = filepath.with_suffix('.json')
        
        with open(graph_file, 'w') as f:
            json.dump(self.knowledge_graph, f, indent=2)
        
        self.log(f"Knowledge graph saved: {graph_file}")
    
    def run_forever(self, seed_topics: List[str]):
        """
        Run continuous research cycles.
        
        Takes list of seed topics, researches each,
        then generates new topics based on discoveries.
        """
        
        self.log("="*60)
        self.log("KNOWLEDGE ARCHAEOLOGY - CONTINUOUS MODE")
        self.log("="*60)
        
        topics_queue = seed_topics.copy()
        researched = set()
        
        cycle = 0
        
        while topics_queue:
            cycle += 1
            
            topic = topics_queue.pop(0)
            
            if topic in researched:
                continue
            
            self.log(f"\n{'='*60}")
            self.log(f"CYCLE {cycle}: {topic}")
            self.log(f"{'='*60}\n")
            
            # Research this topic
            report = self.research_cycle(topic, depth=3)
            
            researched.add(topic)
            
            # Extract new topics from discoveries
            new_topics = self.extract_new_topics()
            
            # Add to queue
            for new_topic in new_topics:
                if new_topic not in researched and new_topic not in topics_queue:
                    topics_queue.append(new_topic)
                    self.log(f"Added to queue: {new_topic}")
            
            self.log(f"\nQueue size: {len(topics_queue)}")
            self.log(f"Researched: {len(researched)}")
        
        self.log("\n" + "="*60)
        self.log("RESEARCH COMPLETE")
        self.log(f"Total cycles: {cycle}")
        self.log(f"Total topics researched: {len(researched)}")
        self.log("="*60)
    
    def extract_new_topics(self) -> List[str]:
        """Extract new research topics from current discoveries"""
        
        new_topics = []
        
        # Topics from frequently appearing concepts
        concept_counts = {}
        for node_id, node in self.knowledge_graph['nodes'].items():
            if node['type'] == 'concept':
                concept_counts[node['name']] = len(node.get('appearances', []))
        
        # Top concepts that haven't been researched yet
        top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
        
        for concept, count in top_concepts[:5]:
            if count >= 2:  # Appears at least twice
                new_topics.append(concept)
        
        return new_topics


# ═══════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════

if __name__ == '__main__':
    
    # Initialize
    archaeologist = KnowledgeArchaeology()
    
    # Seed topics (ancient knowledge domains)
    seed_topics = [
        "Hermetic Philosophy",
        "Ancient Alchemy", 
        "Pythagorean Mathematics",
        "Vedic Science",
        "Taoist Internal Arts"
    ]
    
    # Run continuous research
    archaeologist.run_forever(seed_topics)
