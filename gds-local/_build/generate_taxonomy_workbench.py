#!/usr/bin/env python3
"""
Generates gds-local/_build/_pages/taxonomy-mapping.html
Combines front matter, responsive GOV.UK 3-pane workbench HTML, CSS, and embedded
taxonomy datasets (mappings, hierarchy, powers & duties) for zero-dependency client execution.
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GDS_LOCAL_DIR = os.path.dirname(SCRIPT_DIR)
TAXONOMY_DIR = os.path.join(GDS_LOCAL_DIR, "resources", "taxonomy")
OUTPUT_PAGE = os.path.join(SCRIPT_DIR, "_pages", "taxonomy-mapping.html")

def load_json(filename):
    path = os.path.join(TAXONOMY_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_workbench_page():
    print("Loading taxonomy resources...")
    mapping_data = load_json("lgam-to-esd-mapping.json")
    hierarchy_data = load_json("esd-functions-hierarchy.json")
    powers_duties_raw = load_json("esd-powers-and-duties.json")

    # Clean and compact powers and duties
    pd_items = powers_duties_raw.get("list", {}).get("items", [])
    compact_pd = []
    for item in pd_items:
        t = "duty" if "/duty/" in item.get("uri", "") else "power"
        compact_pd.append({
            "id": item.get("identifier", ""),
            "label": item.get("label", ""),
            "desc": item.get("description", ""),
            "type": t,
            "uri": item.get("uri", "")
        })

    print(f"Loaded: {len(mapping_data.get('mappings', {}))} domains, {len(hierarchy_data)} functions, {len(compact_pd)} powers/duties.")

    json_mapping_str = json.dumps(mapping_data, separators=(',', ':'))
    json_hierarchy_str = json.dumps(hierarchy_data, separators=(',', ':'))
    json_pd_str = json.dumps(compact_pd, separators=(',', ':'))

    html_content = f'''---
title: "Taxonomy Mapping Workbench"
description: "Interactive workbench for visualising, curating, and exporting mappings between LGAM domains and official ESD statutory functions and services."
category: "Tools & Governance"
layout: "full-width"
---
<style>
  /* Base & Layout Overrides */
  .app-main-content {{
    max-width: 1440px !important;
    padding: 24px 32px !important;
  }}

  /* Top Stat & Notification Bar */
  .workbench-header-bar {{
    background: #f3f2f1;
    border-left: 6px solid #1d70b8;
    padding: 16px 20px;
    margin-bottom: 24px;
    border-radius: 2px;
  }}

  .workbench-stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-top: 14px;
  }}

  .workbench-stat-card {{
    background: #ffffff;
    padding: 12px 16px;
    border: 1px solid #b1b4b6;
    border-radius: 4px;
  }}

  .workbench-stat-number {{
    font-size: 24px;
    font-weight: 700;
    color: #0b0c0c;
    line-height: 1.1;
    display: block;
  }}

  .workbench-stat-label {{
    font-size: 13px;
    color: #505a5f;
    margin-top: 4px;
    display: block;
  }}

  /* Draft Recovery Alert */
  .workbench-draft-banner {{
    display: none;
    background: #fff7d7;
    border-left: 6px solid #ffdd00;
    padding: 12px 16px;
    margin-bottom: 20px;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    border-radius: 2px;
  }}
  .workbench-draft-banner.is-active {{
    display: flex;
  }}

  /* 3-Pane Grid Architecture */
  .workbench-layout-grid {{
    display: grid;
    grid-template-columns: 310px minmax(420px, 1.2fr) minmax(380px, 1fr);
    gap: 20px;
    align-items: stretch;
    min-height: 780px;
  }}

  @media (max-width: 1280px) {{
    .workbench-layout-grid {{
      grid-template-columns: 280px 1fr;
    }}
    .workbench-pane--inspector {{
      grid-column: 1 / -1;
    }}
  }}

  @media (max-width: 860px) {{
    .workbench-layout-grid {{
      grid-template-columns: 1fr;
    }}
  }}

  /* Shared Pane Card Style */
  .workbench-pane {{
    background: #ffffff;
    border: 1px solid #b1b4b6;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    overflow: hidden;
  }}

  .workbench-pane-header {{
    padding: 16px;
    background: #f8f8f8;
    border-bottom: 1px solid #d8d8d8;
  }}

  .workbench-pane-body {{
    padding: 16px;
    flex: 1;
    overflow-y: auto;
    /* max-height removed to fix clipping */
    min-height: 520px;
  }}

  .workbench-pane-footer {{
    padding: 12px 16px;
    background: #f8f8f8;
    border-top: 1px solid #d8d8d8;
  }}

  /* Left Pane: Domain Selector */
  .domain-search-box {{
    margin-bottom: 12px;
  }}

  .domain-filter-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
  }}

  .domain-filter-pill {{
    background: #e5e5e5;
    border: 1px solid #b1b4b6;
    padding: 3px 8px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border-radius: 12px;
    color: #0b0c0c;
    transition: all 0.15s ease;
  }}

  .domain-filter-pill:hover {{
    background: #d8d8d8;
  }}

  .domain-filter-pill.is-selected {{
    background: #1d70b8;
    color: #ffffff;
    border-color: #1d70b8;
  }}

  .domain-list {{
    list-style: none;
    margin: 0;
    padding: 0;
  }}

  .domain-item {{
    border-bottom: 1px solid #e5e5e5;
    padding: 10px 12px;
    cursor: pointer;
    transition: background 0.15s ease, border-left 0.15s ease;
    border-left: 4px solid transparent;
  }}

  .domain-item:hover {{
    background: #f3f8fc;
  }}

  .domain-item.is-active {{
    background: #edf4fa;
    border-left-color: #1d70b8;
  }}

  .domain-item-title {{
    font-size: 14px;
    font-weight: 700;
    color: #0b0c0c;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }}

  .domain-item-meta {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #505a5f;
  }}

  .domain-type-badge {{
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }}

  .domain-type-badge--ba {{
    background: #e8f0f8;
    color: #0000ff;
    border: 1px solid #bfd3ee;
  }}

  .domain-type-badge--ca {{
    background: #f0f0f0;
    color: #505a5f;
    border: 1px solid #cccccc;
  }}

  .domain-status-tag {{
    font-size: 11px;
    padding: 2px 6px;
    font-weight: 600;
    border-radius: 3px;
    display: inline-block;
  }}

  .domain-status-tag--mapped {{
    background: #cce2d8;
    color: #005a30;
  }}

  .domain-status-tag--modified {{
    background: #fff7bf;
    color: #594d00;
  }}

  .domain-status-tag--unmapped {{
    background: #e5e5e5;
    color: #505a5f;
  }}

  /* Centre Pane: Workbench */
  .workbench-domain-header {{
    border-bottom: 2px solid #1d70b8;
    padding-bottom: 12px;
    margin-bottom: 16px;
  }}

  .workbench-domain-title {{
    margin: 0 0 6px 0;
    font-size: 22px;
    font-weight: 700;
    color: #0b0c0c;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }}

  .curator-notes-card {{
    background: #fbfbfb;
    border: 1px solid #d8d8d8;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 20px;
  }}

  .curator-notes-title {{
    font-size: 13px;
    font-weight: 700;
    color: #0b0c0c;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  .curator-notes-textarea {{
    width: 100%;
    box-sizing: border-box;
    font-family: inherit;
    font-size: 13px;
    padding: 8px;
    border: 1px solid #b1b4b6;
    border-radius: 2px;
    resize: vertical;
    min-height: 56px;
  }}

  /* Autocomplete Mapping Action Bar */
  .function-search-container {{
    position: relative;
    margin-bottom: 20px;
  }}

  .function-autocomplete-menu {{
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #ffffff;
    border: 2px solid #1d70b8;
    border-top: none;
    max-height: 280px;
    overflow-y: auto;
    z-index: 100;
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    display: none;
  }}

  .function-autocomplete-menu.is-open {{
    display: block;
  }}

  .autocomplete-item {{
    padding: 10px 14px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .autocomplete-item:hover, .autocomplete-item.is-focused {{
    background: #1d70b8;
    color: #ffffff;
  }}

  .autocomplete-item:hover .autocomplete-sub,
  .autocomplete-item.is-focused .autocomplete-sub {{
    color: #e0f0ff;
  }}

  .autocomplete-sub {{
    font-size: 12px;
    color: #505a5f;
    margin-top: 2px;
  }}

  /* Mapped Functions Cards */
  .mapped-functions-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }}

  .mapped-function-card {{
    background: #ffffff;
    border: 1px solid #b1b4b6;
    border-left: 4px solid #1d70b8;
    border-radius: 4px;
    margin-bottom: 12px;
    transition: box-shadow 0.15s ease;
  }}

  .mapped-function-card:hover {{
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  }}

  .function-card-header {{
    padding: 12px 14px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
  }}

  .function-card-title {{
    font-size: 15px;
    font-weight: 700;
    color: #0b0c0c;
    margin: 0 0 4px 0;
  }}

  .function-card-meta {{
    font-size: 12px;
    color: #505a5f;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}

  .function-actions {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }}

  .btn-action-small {{
    background: #f3f2f1;
    border: 1px solid #b1b4b6;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border-radius: 3px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    color: #0b0c0c;
    text-decoration: none;
    transition: all 0.15s ease;
  }}

  .btn-action-small:hover {{
    background: #e5e5e5;
  }}

  .btn-action-small--unmap:hover {{
    background: #f8d7da;
    border-color: #d4351c;
    color: #d4351c;
  }}

  .btn-action-small--inspect {{
    background: #e8f0f8;
    border-color: #1d70b8;
    color: #1d70b8;
  }}
  .btn-action-small--inspect:hover {{
    background: #1d70b8;
    color: #ffffff;
  }}

  /* Collapsible Services Accordion */
  .function-services-tray {{
    border-top: 1px solid #eee;
    background: #fafafa;
    padding: 10px 14px;
  }}

  .services-toggle-btn {{
    background: none;
    border: none;
    padding: 0;
    color: #1d70b8;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}

  .services-toggle-btn:hover {{
    text-decoration: underline;
  }}

  .services-list-collapsible {{
    margin-top: 8px;
    display: none;
  }}

  .services-list-collapsible.is-expanded {{
    display: block;
  }}

  .service-chip-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
  }}

  .service-chip {{
    background: #ffffff;
    border: 1px solid #d8d8d8;
    padding: 3px 8px;
    font-size: 12px;
    border-radius: 3px;
    color: #0b0c0c;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}

  .service-chip-id {{
    font-family: monospace;
    font-size: 11px;
    color: #505a5f;
    font-weight: 600;
  }}

  /* Right Pane: Inspector & Export Tabs */
  .inspector-tabs-nav {{
    display: flex;
    border-bottom: 2px solid #b1b4b6;
    margin-bottom: 16px;
    background: #f8f8f8;
  }}

  .inspector-tab-btn {{
    flex: 1;
    background: none;
    border: none;
    padding: 12px 14px;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    color: #505a5f;
    border-bottom: 4px solid transparent;
    margin-bottom: -2px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.15s ease;
  }}

  .inspector-tab-btn:hover {{
    background: #ececec;
    color: #0b0c0c;
  }}

  .inspector-tab-btn.is-active {{
    background: #ffffff;
    color: #1d70b8;
    border-bottom-color: #1d70b8;
  }}

  .tab-badge {{
    background: #1d70b8;
    color: #ffffff;
    font-size: 11px;
    padding: 1px 6px;
    border-radius: 10px;
    font-weight: 600;
  }}

  .tab-badge--warning {{
    background: #ffdd00;
    color: #0b0c0c;
  }}

  .tab-pane-content {{
    display: none;
  }}

  .tab-pane-content.is-active {{
    display: block;
  }}

  /* Reference Inspector Details */
  .inspector-detail-box {{
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
    padding: 12px 14px;
    border-radius: 4px;
    margin-bottom: 16px;
  }}

  .inspector-detail-label {{
    font-size: 11px;
    font-weight: 700;
    color: #505a5f;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
    display: block;
  }}

  .inspector-detail-value {{
    font-size: 13px;
    color: #0b0c0c;
    line-height: 1.4;
  }}

  .hierarchy-trail {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    margin-top: 4px;
  }}

  .hierarchy-step {{
    background: #e8f0f8;
    border: 1px solid #bfd3ee;
    padding: 2px 6px;
    border-radius: 3px;
    color: #1d70b8;
    font-weight: 600;
  }}

  .hierarchy-sep {{
    color: #505a5f;
    font-size: 10px;
  }}

  /* Statutory Powers & Duties List in Inspector */
  .pd-search-box {{
    margin-bottom: 12px;
  }}

  .pd-type-filters {{
    display: flex;
    gap: 6px;
    margin-bottom: 12px;
  }}

  .pd-type-pill {{
    background: #e5e5e5;
    border: 1px solid #b1b4b6;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    border-radius: 10px;
    color: #0b0c0c;
  }}

  .pd-type-pill.is-selected {{
    background: #1d70b8;
    color: #ffffff;
    border-color: #1d70b8;
  }}

  .pd-list-container {{
    max-height: 360px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}

  .pd-card {{
    background: #ffffff;
    border: 1px solid #d8d8d8;
    border-left: 3px solid #1d70b8;
    padding: 10px 12px;
    border-radius: 3px;
    font-size: 12px;
  }}

  .pd-card--power {{
    border-left-color: #00703c;
  }}

  .pd-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 4px;
  }}

  .pd-tag {{
    font-size: 10px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 2px;
    text-transform: uppercase;
  }}

  .pd-tag--duty {{
    background: #1d70b8;
    color: #ffffff;
  }}

  .pd-tag--power {{
    background: #00703c;
    color: #ffffff;
  }}

  .pd-card-title {{
    font-weight: 700;
    color: #0b0c0c;
    font-size: 13px;
  }}

  .pd-card-desc {{
    color: #505a5f;
    line-height: 1.35;
    margin-top: 4px;
  }}

  /* Tab 2: Export & Review Hub */
  .diff-summary-panel {{
    background: #f8f8f8;
    border: 1px solid #b1b4b6;
    padding: 14px;
    border-radius: 4px;
    margin-bottom: 16px;
  }}

  .diff-stat-line {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 6px;
  }}

  .diff-stat-line:last-child {{
    margin-bottom: 0;
  }}

  .diff-list-container {{
    max-height: 280px;
    overflow-y: auto;
    margin-bottom: 16px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 8px;
    background: #ffffff;
  }}

  .diff-domain-item {{
    border-bottom: 1px solid #eee;
    padding: 8px;
    font-size: 12px;
  }}

  .diff-domain-item:last-child {{
    border-bottom: none;
  }}

  .diff-item-add {{
    color: #00703c;
    font-weight: 600;
  }}

  .diff-item-remove {{
    color: #d4351c;
    font-weight: 600;
  }}

  .diff-item-note {{
    color: #1d70b8;
    font-style: italic;
  }}

  .export-actions-stack {{
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  /* Modal System */
  .lgam-modal-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.6);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    padding: 20px;
  }}

  .lgam-modal-overlay.is-active {{
    display: flex;
  }}

  .lgam-modal-content {{
    background: #ffffff;
    max-width: 680px;
    width: 100%;
    max-height: 80vh;
    border-radius: 4px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}

  .lgam-modal-header {{
    padding: 16px 20px;
    background: #f8f8f8;
    border-bottom: 1px solid #d8d8d8;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .lgam-modal-body {{
    padding: 20px;
    overflow-y: auto;
    flex: 1;
  }}

  .lgam-modal-footer {{
    padding: 14px 20px;
    background: #f8f8f8;
    border-top: 1px solid #d8d8d8;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }}

  /* Toast Notification */
  .workbench-toast {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #0b0c0c;
    color: #ffffff;
    padding: 12px 20px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    z-index: 10000;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.25s ease;
    pointer-events: none;
  }}

  .workbench-toast.is-visible {{
    opacity: 1;
    transform: translateY(0);
  }}

  .workbench-toast--success {{
    background: #00703c;
  }}
  .workbench-toast--info {{
    background: #1d70b8;
  }}
  .workbench-toast--warning {{
    background: #f47738;
  }}
</style>

<nav-contents>
  <li class="app-navigation__item"><a class="app-navigation__link" href="#workbench-overview">Workbench Overview</a></li>
  <li class="app-navigation__item"><a class="app-navigation__link" href="#domain-mapping-tool">Domain Mapping Tool</a></li>
  <li class="app-navigation__item"><a class="app-navigation__link" href="#reference-inspector-heading">Reference Inspector</a></li>
  <li class="app-navigation__item"><a class="app-navigation__link" href="#export-hub-heading">Export & Diff Hub</a></li>
  <li class="app-navigation__item"><a class="app-navigation__link" href="#curation-guidance">Curation Standards</a></li>
</nav-contents>

<main-content>
  <span class="govuk-caption-xl">Tools & Governance</span>
  <h1 class="govuk-heading-xl" id="workbench-overview">Taxonomy Mapping Workbench</h1>

  <p class="govuk-body-l">
    Interactive governance workbench for visualising, curating, and exporting programmatic mappings between the LGAM 9-Layer Architecture domains (12 Business Areas &amp; 10 Corporate Areas) and the LGA / ESD official local government service taxonomy.
  </p>

  <!-- Top Metrics Bar -->
  <div class="workbench-header-bar">
    <div class="govuk-!-margin-bottom-2">
      <strong class="govuk-tag govuk-tag--blue">ESD Standards 2026</strong>
      <span class="govuk-body-s govuk-!-margin-left-2" style="color:#505a5f;">Source: Local Government Association / LG Inform Plus</span>
    </div>
    
    <div class="workbench-stats-grid">
      <div class="workbench-stat-card">
        <span class="workbench-stat-number" id="stat-domains-count">22</span>
        <span class="workbench-stat-label">LGAM Domains (12 BA / 10 CA)</span>
      </div>
      <div class="workbench-stat-card">
        <span class="workbench-stat-number" id="stat-functions-count">176</span>
        <span class="workbench-stat-label">ESD Functions Pool</span>
      </div>
      <div class="workbench-stat-card">
        <span class="workbench-stat-number" id="stat-services-count">210</span>
        <span class="workbench-stat-label">ESD Standard Services</span>
      </div>
      <div class="workbench-stat-card">
        <span class="workbench-stat-number" id="stat-pd-count">4,025</span>
        <span class="workbench-stat-label">Statutory Powers &amp; Duties</span>
      </div>
      <div class="workbench-stat-card">
        <span class="workbench-stat-number" id="stat-unmapped-count">0</span>
        <span class="workbench-stat-label">Unmapped ESD Functions</span>
      </div>
    </div>
  </div>

  <!-- Draft Recovery Banner -->
  <div class="workbench-draft-banner" id="draft-recovery-banner" role="alert">
    <div>
      <strong class="govuk-body-s" style="font-weight:700;">Working Draft Restored:</strong>
      <span class="govuk-body-s" id="draft-banner-message">You have uncommitted taxonomy curation changes stored in your local browser session.</span>
    </div>
    <div style="display:flex; gap:8px;">
      <button class="govuk-button govuk-button--secondary govuk-!-margin-bottom-0" style="padding:4px 10px; font-size:12px;" onclick="WorkbenchApp.discardDraft()">Discard Draft</button>
      <button class="govuk-button govuk-!-margin-bottom-0" style="padding:4px 10px; font-size:12px;" onclick="WorkbenchApp.switchTab('export')">Review &amp; Export</button>
    </div>
  </div>

  <!-- Main 3-Pane Workbench Interface -->
  <div class="workbench-layout-grid" id="domain-mapping-tool">
    
    <!-- LEFT PANE: DOMAIN SELECTOR -->
    <section class="workbench-pane workbench-pane--domains" aria-label="LGAM Domain Selector">
      <div class="workbench-pane-header">
        <h2 class="govuk-heading-s govuk-!-margin-bottom-2">LGAM Domains</h2>
        
        <div class="domain-search-box">
          <label class="govuk-visually-hidden" for="domain-search-input">Filter LGAM Domains</label>
          <input type="search" id="domain-search-input" class="govuk-input govuk-input--extra-letter-spacing" placeholder="Filter 22 domains..." oninput="WorkbenchApp.onDomainSearch(this.value)">
        </div>

        <div class="domain-filter-pills" role="tablist" aria-label="Domain Category Filter">
          <button class="domain-filter-pill is-selected" data-filter="all" onclick="WorkbenchApp.setDomainFilter('all')">All (22)</button>
          <button class="domain-filter-pill" data-filter="ba" onclick="WorkbenchApp.setDomainFilter('ba')">Business (12)</button>
          <button class="domain-filter-pill" data-filter="ca" onclick="WorkbenchApp.setDomainFilter('ca')">Corporate (10)</button>
          <button class="domain-filter-pill" data-filter="modified" onclick="WorkbenchApp.setDomainFilter('modified')">Modified <span id="filter-modified-count">(0)</span></button>
        </div>
      </div>

      <div class="workbench-pane-body" style="padding:0;">
        <ul class="domain-list" id="domain-list-container" role="listbox" aria-label="LGAM Domains List">
          <!-- Populated dynamically by JS -->
        </ul>
      </div>

      <div class="workbench-pane-footer">
        <button class="govuk-button govuk-button--secondary govuk-!-margin-bottom-0" style="width:100%; font-size:13px; padding:6px 10px;" onclick="WorkbenchApp.openUnmappedPoolModal()">
          <span id="unmapped-pool-btn-label">Unmapped ESD Pool (0)</span>
        </button>
      </div>
    </section>

    <!-- CENTRE PANE: WORKBENCH -->
    <section class="workbench-pane workbench-pane--curator" aria-label="Domain Mapping Workbench">
      <div class="workbench-pane-body" id="curator-workbench-container">
        <!-- Dynamically rendered domain editor -->
      </div>
    </section>

    <!-- RIGHT PANE: TABBED INSPECTOR & EXPORT HUB -->
    <section class="workbench-pane workbench-pane--inspector" aria-label="Reference Inspector and Export Hub">
      <div class="inspector-tabs-nav" role="tablist">
        <button class="inspector-tab-btn is-active" id="tab-btn-inspector" role="tab" aria-selected="true" aria-controls="tab-content-inspector" onclick="WorkbenchApp.switchTab('inspector')">
          <span>Reference Inspector</span>
        </button>
        <button class="inspector-tab-btn" id="tab-btn-export" role="tab" aria-selected="false" aria-controls="tab-content-export" onclick="WorkbenchApp.switchTab('export')">
          <span>Export &amp; Review</span>
          <span class="tab-badge" id="export-diff-badge" style="display:none;">0</span>
        </button>
      </div>

      <div class="workbench-pane-body">
        <!-- Tab 1: Reference Inspector -->
        <div class="tab-pane-content is-active" id="tab-content-inspector" role="tabpanel" aria-labelledby="tab-btn-inspector">
          <h2 class="govuk-visually-hidden" id="reference-inspector-heading">Reference Inspector</h2>
          <div id="inspector-body-container">
            <!-- Dynamically populated function details and powers/duties -->
          </div>
        </div>

        <!-- Tab 2: Export & Review Hub -->
        <div class="tab-pane-content" id="tab-content-export" role="tabpanel" aria-labelledby="tab-btn-export">
          <h2 class="govuk-heading-m govuk-!-margin-bottom-2" id="export-hub-heading">Export &amp; Review Hub</h2>
          <p class="govuk-body-s" style="color:#505a5f;">
            Track live curation differences against baseline mapping and generate schema-compliant JSON/CSV artifacts.
          </p>

          <div class="diff-summary-panel">
            <h3 class="govuk-heading-s govuk-!-margin-bottom-2">Live Curation Diff</h3>
            <div class="diff-stat-line">
              <span>Modified Domains:</span>
              <strong id="diff-domains-stat">0</strong>
            </div>
            <div class="diff-stat-line">
              <span>Mapped Functions Added:</span>
              <strong class="diff-item-add" id="diff-added-stat">+0</strong>
            </div>
            <div class="diff-stat-line">
              <span>Mapped Functions Removed:</span>
              <strong class="diff-item-remove" id="diff-removed-stat">-0</strong>
            </div>
            <div class="diff-stat-line">
              <span>Curator Notes Updated:</span>
              <strong class="diff-item-note" id="diff-notes-stat">0</strong>
            </div>
          </div>

          <h3 class="govuk-heading-s govuk-!-margin-bottom-2">Change Log Details</h3>
          <div class="diff-list-container" id="diff-details-container">
            <div style="color:#505a5f; font-size:12px; text-align:center; padding:16px;">
              No curation modifications yet. Working state matches baseline taxonomy mapping.
            </div>
          </div>

          <div class="export-actions-stack">
            <button class="govuk-button govuk-!-margin-bottom-0" onclick="WorkbenchApp.downloadJson()">
              Download JSON (Schema Compliant)
            </button>
            <button class="govuk-button govuk-button--secondary govuk-!-margin-bottom-0" onclick="WorkbenchApp.downloadCsv()">
              Download CSV (Matrix View)
            </button>
            <button class="govuk-button govuk-button--secondary govuk-!-margin-bottom-0" onclick="WorkbenchApp.copyJsonToClipboard()">
              Copy JSON to Clipboard
            </button>
            <button class="govuk-button govuk-button--warning govuk-!-margin-bottom-0" onclick="WorkbenchApp.promptResetBaseline()">
              Reset to Baseline Mapping
            </button>
          </div>
        </div>
      </div>
    </section>

  </div>

  <!-- Guidance Section -->
  <hr class="govuk-section-break govuk-section-break--xl govuk-section-break--visible">
  <div id="curation-guidance">
    <h2 class="govuk-heading-l">Taxonomy Curation Standards</h2>
    <div class="govuk-grid-row">
      <div class="govuk-grid-column-one-half">
        <h3 class="govuk-heading-s">ESD Function Hierarchy Alignment</h3>
        <p class="govuk-body">
          Each LGAM domain links to official ESD Functions (level 2/3 hierarchy nodes). Functions inherit all child standard services defined under them in the LGA standards registry. Adding a function automatically links all associated child statutory services.
        </p>
      </div>
      <div class="govuk-grid-column-one-half">
        <h3 class="govuk-heading-s">Statutory Powers &amp; Duties Governance</h3>
        <p class="govuk-body">
          Local authorities deliver services under explicit statutory powers (discretionary) and duties (mandatory). Use the Reference Inspector to audit the legal authority underpinning each mapped function before publishing enterprise architecture patterns.
        </p>
      </div>
    </div>
  </div>

  <!-- MODAL: UNMAPPED FUNCTIONS POOL -->
  <div class="lgam-modal-overlay" id="unmapped-pool-modal" role="dialog" aria-modal="true" aria-labelledby="unmapped-modal-title">
    <div class="lgam-modal-content">
      <div class="lgam-modal-header">
        <h2 class="govuk-heading-s govuk-!-margin-bottom-0" id="unmapped-modal-title">Unmapped ESD Functions Pool</h2>
        <button class="btn-action-small" onclick="WorkbenchApp.closeUnmappedPoolModal()" aria-label="Close modal">✕</button>
      </div>
      <div class="lgam-modal-body">
        <p class="govuk-body-s" style="color:#505a5f;">
          The following official ESD Functions are currently not mapped to any of the 22 LGAM domains. You can assign any function directly to the currently selected domain: <strong id="modal-current-domain-name">Adult social care</strong>.
        </p>
        <div id="unmapped-functions-list" style="display:flex; flex-direction:column; gap:8px;">
          <!-- Populated by JS -->
        </div>
      </div>
      <div class="lgam-modal-footer">
        <button class="govuk-button govuk-button--secondary govuk-!-margin-bottom-0" onclick="WorkbenchApp.closeUnmappedPoolModal()">Close</button>
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION -->
  <div class="workbench-toast" id="workbench-toast" role="status" aria-live="polite">
    Notification message
  </div>

</main-content>

<page-script>
(function() {{
  // EMBEDDED TAXONOMY DATASETS
  const BASELINE_MAPPING = {json_mapping_str};
  const ESD_HIERARCHY = {json_hierarchy_str};
  const ESD_POWERS_DUTIES = {json_pd_str};

  const STORAGE_KEY = "lgam_taxonomy_workbench_draft";

  // Application State
  const state = {{
    workingMapping: JSON.parse(JSON.stringify(BASELINE_MAPPING.mappings)),
    currentDomainId: "FG_AdultSocial",
    inspectedFunctionId: "148", // Default to Adult Social Care function
    activeTab: "inspector",
    domainSearchTerm: "",
    domainCategoryFilter: "all",
    expandedServices: {{}},
    pdSearchTerm: "",
    pdFilterType: "all",
    focusedAutocompleteIndex: -1,
    hasDraftSaved: false,
    functionNotes: JSON.parse(localStorage.getItem('lgam_function_notes') || '{{}}')
  }};

  // Helper: Deep Clone
  function deepClone(obj) {{
    return JSON.parse(JSON.stringify(obj));
  }}

  // Helper: Toast
  function showToast(message, type = "info") {{
    const toast = document.getElementById("workbench-toast");
    if (!toast) return;
    toast.textContent = message;
    toast.className = `workbench-toast workbench-toast--${{type}} is-visible`;
    setTimeout(() => {{
      toast.className = "workbench-toast";
    }}, 3200);
  }}

  // Persistence: Save to LocalStorage
  function saveToLocalStorage() {{
    try {{
      const draftPayload = {{
        timestamp: new Date().toISOString(),
        mappings: state.workingMapping
      }};
      localStorage.setItem(STORAGE_KEY, JSON.stringify(draftPayload));
      localStorage.setItem('lgam_function_notes', JSON.stringify(state.functionNotes));
      updateDraftStatusBanner();
      updateDiffMetrics();
      renderDomainList();
    }} catch (e) {{
      console.error("LocalStorage save error:", e);
    }}
  }}

  // Persistence: Check & Load Draft
  function initDraftPersistence() {{
    try {{
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {{
        const parsed = JSON.parse(saved);
        if (parsed && parsed.mappings) {{
          state.workingMapping = parsed.mappings;
          state.hasDraftSaved = true;
          const banner = document.getElementById("draft-recovery-banner");
          const msg = document.getElementById("draft-banner-message");
          if (banner && msg) {{
            const dateStr = parsed.timestamp ? new Date(parsed.timestamp).toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}}) : "earlier";
            msg.textContent = `Draft restored from your local session (${{dateStr}}). Unexported modifications are active.`;
            banner.classList.add("is-active");
          }}
        }}
      }}
    }} catch (e) {{
      console.warn("Could not parse saved draft:", e);
    }}
  }}

  // Compute Diff between workingMapping and BASELINE_MAPPING
  function calculateDiff() {{
    const base = BASELINE_MAPPING.mappings;
    const work = state.workingMapping;
    const diff = {{
      domainsModified: 0,
      totalAdded: 0,
      totalRemoved: 0,
      notesUpdated: 0,
      details: []
    }};

    for (const domainId in base) {{
      const baseDomain = base[domainId];
      const workDomain = work[domainId] || {{ functions: [], curator_notes: "" }};

      const baseFns = new Map((baseDomain.functions || []).map(f => [String(f.function_id), f.label]));
      const workFns = new Map((workDomain.functions || []).map(f => [String(f.function_id), f.label]));

      const added = [];
      const removed = [];

      for (const [fid, flabel] of workFns.entries()) {{
        if (!baseFns.has(fid)) {{
          added.push({{ id: fid, label: flabel }});
        }}
      }}

      for (const [fid, flabel] of baseFns.entries()) {{
        if (!workFns.has(fid)) {{
          removed.push({{ id: fid, label: flabel }});
        }}
      }}

      const baseNotes = (baseDomain.curator_notes || "").trim();
      const workNotes = (workDomain.curator_notes || "").trim();
      const noteChanged = baseNotes !== workNotes;

      if (added.length > 0 || removed.length > 0 || noteChanged) {{
        diff.domainsModified++;
        diff.totalAdded += added.length;
        diff.totalRemoved += removed.length;
        if (noteChanged) diff.notesUpdated++;

        diff.details.push({{
          domainId: domainId,
          domainName: baseDomain.name,
          domainType: baseDomain.type,
          added: added,
          removed: removed,
          noteChanged: noteChanged,
          workNotes: workNotes
        }});
      }}
    }}

    return diff;
  }}

  function updateDraftStatusBanner() {{
    const diff = calculateDiff();
    const banner = document.getElementById("draft-recovery-banner");
    const diffBadge = document.getElementById("export-diff-badge");
    const filterModifiedCount = document.getElementById("filter-modified-count");

    if (filterModifiedCount) {{
      filterModifiedCount.textContent = `(${{diff.domainsModified}})`;
    }}

    if (diff.domainsModified > 0) {{
      if (banner) banner.classList.add("is-active");
      if (diffBadge) {{
        diffBadge.textContent = diff.domainsModified;
        diffBadge.style.display = "inline-block";
        diffBadge.className = "tab-badge tab-badge--warning";
      }}
    }} else {{
      if (diffBadge) diffBadge.style.display = "none";
    }}
  }}

  function updateDiffMetrics() {{
    const diff = calculateDiff();
    const domStat = document.getElementById("diff-domains-stat");
    const addStat = document.getElementById("diff-added-stat");
    const remStat = document.getElementById("diff-removed-stat");
    const noteStat = document.getElementById("diff-notes-stat");
    const detailsContainer = document.getElementById("diff-details-container");

    if (domStat) domStat.textContent = diff.domainsModified;
    if (addStat) addStat.textContent = `+${{diff.totalAdded}}`;
    if (remStat) remStat.textContent = `-${{diff.totalRemoved}}`;
    if (noteStat) noteStat.textContent = diff.notesUpdated;

    if (!detailsContainer) return;

    if (diff.details.length === 0) {{
      detailsContainer.innerHTML = `
        <div style="color:#505a5f; font-size:12px; text-align:center; padding:16px;">
          No curation modifications yet. Working state matches baseline taxonomy mapping.
        </div>
      `;
      return;
    }}

    let html = "";
    diff.details.forEach(d => {{
      html += `
        <div class="diff-domain-item">
          <strong style="font-size:13px; color:#0b0c0c;">${{d.domainName}}</strong>
          <span style="font-size:11px; color:#505a5f;">(${{d.domainId}})</span>
          <div style="margin-top:4px;">
      `;

      d.added.forEach(a => {{
        html += `<div class="diff-item-add">+ Added Function [ESD-${{a.id}}] ${{a.label}}</div>`;
      }});

      d.removed.forEach(r => {{
        html += `<div class="diff-item-remove">- Removed Function [ESD-${{r.id}}] ${{r.label}}</div>`;
      }});

      if (d.noteChanged) {{
        html += `<div class="diff-item-note">✎ Curator note updated: "${{d.workNotes ? (d.workNotes.substring(0, 40) + '...') : '[Cleared]'}}"</div>`;
      }}

      html += `</div></div>`;
    }});

    detailsContainer.innerHTML = html;
  }}

  // Unmapped Functions Pool Calculation
  function getUnmappedFunctions() {{
    const allFunctionIds = Object.keys(ESD_HIERARCHY);
    const mappedFunctionIds = new Set();

    for (const dId in state.workingMapping) {{
      const d = state.workingMapping[dId];
      (d.functions || []).forEach(f => mappedFunctionIds.add(String(f.function_id)));
    }}

    return allFunctionIds
      .filter(id => !mappedFunctionIds.has(String(id)))
      .map(id => ESD_HIERARCHY[id]);
  }}

  function updateGlobalCounters() {{
    const unmapped = getUnmappedFunctions();
    const unmappedStat = document.getElementById("stat-unmapped-count");
    const unmappedBtn = document.getElementById("unmapped-pool-btn-label");

    if (unmappedStat) unmappedStat.textContent = unmapped.length;
    if (unmappedBtn) unmappedBtn.textContent = `Unmapped ESD Pool (${{unmapped.length}})`;
  }}

  // DOMAIN LIST RENDERING
  function renderDomainList() {{
    const container = document.getElementById("domain-list-container");
    if (!container) return;

    const diff = calculateDiff();
    const modifiedDomainIds = new Set(diff.details.map(d => d.domainId));

    let domains = Object.keys(state.workingMapping).map(dId => ({{
      id: dId,
      ...state.workingMapping[dId]
    }}));

    // Category filter
    if (state.domainCategoryFilter === "ba") {{
      domains = domains.filter(d => d.type === "BusinessArea");
    }} else if (state.domainCategoryFilter === "ca") {{
      domains = domains.filter(d => d.type === "CorporateArea");
    }} else if (state.domainCategoryFilter === "modified") {{
      domains = domains.filter(d => modifiedDomainIds.has(d.id));
    }}

    // Text search
    if (state.domainSearchTerm) {{
      const term = state.domainSearchTerm.toLowerCase();
      domains = domains.filter(d => 
        d.name.toLowerCase().includes(term) || 
        d.id.toLowerCase().includes(term)
      );
    }}

    if (domains.length === 0) {{
      container.innerHTML = `
        <li style="padding:16px; font-size:13px; color:#505a5f; text-align:center;">
          No domains match filter.
        </li>
      `;
      return;
    }}

    let html = "";
    domains.forEach(d => {{
      const isActive = d.id === state.currentDomainId;
      const isModified = modifiedDomainIds.has(d.id);
      const isBusiness = d.type === "BusinessArea";
      const fnCount = (d.functions || []).length;
      const svcCount = (d.functions || []).reduce((acc, f) => acc + (f.services ? f.services.length : 0), 0);

      let statusTag = "";
      if (isModified) {{
        statusTag = `<span class="domain-status-tag domain-status-tag--modified">Draft Modified</span>`;
      }} else if (fnCount > 0) {{
        statusTag = `<span class="domain-status-tag domain-status-tag--mapped">Mapped</span>`;
      }} else {{
        statusTag = `<span class="domain-status-tag domain-status-tag--unmapped">Unmapped</span>`;
      }}

      const typeBadge = isBusiness 
        ? `<span class="domain-type-badge domain-type-badge--ba">BA</span>`
        : `<span class="domain-type-badge domain-type-badge--ca">CA</span>`;

      html += `
        <li class="domain-item ${{isActive ? 'is-active' : ''}}" 
            role="option" 
            aria-selected="${{isActive}}"
            tabindex="0"
            onclick="WorkbenchApp.selectDomain('${{d.id}}')">
          <div class="domain-item-title">
            <span>${{d.name}}</span>
            ${{typeBadge}}
          </div>
          <div class="domain-item-meta">
            ${{statusTag}}
            <span>•</span>
            <span>${{fnCount}} fn • ${{svcCount}} svc</span>
          </div>
        </li>
      `;
    }});

    container.innerHTML = html;
  }}


  // CENTRE PANE: WORKBENCH RENDER
  function renderWorkbenchCentre() {{
    const container = document.getElementById("curator-workbench-container");
    if (!container) return;

    const domain = state.workingMapping[state.currentDomainId];
    if (!domain) {{
      container.innerHTML = `<div class="govuk-body">Select a domain from the left.</div>`;
      return;
    }}

    const isBusiness = domain.type === "BusinessArea";
    const mappedFns = domain.functions || [];
    const totalSvcs = mappedFns.reduce((acc, f) => acc + (f.services ? f.services.length : 0), 0);

    // Build reverse map for "Also mapped to"
    const inverseMap = {{}};
    for (const dId in state.workingMapping) {{
      const d = state.workingMapping[dId];
      (d.functions || []).forEach(f => {{
        if (!inverseMap[f.function_id]) inverseMap[f.function_id] = [];
        inverseMap[f.function_id].push({{id: dId, name: d.name}});
      }});
    }}

    let html = `
      <div class="workbench-domain-header">
        <div class="workbench-domain-title">
          <span>${{domain.name}}</span>
          <div>
            <span class="domain-type-badge ${{isBusiness ? 'domain-type-badge--ba' : 'domain-type-badge--ca'}}" style="font-size:12px; padding:3px 8px;">
              ${{isBusiness ? 'Business Area' : 'Corporate Area'}}
            </span>
            <span style="font-family:monospace; font-size:12px; color:#505a5f; margin-left:6px;">[${{domain.domain_id}}]</span>
          </div>
        </div>
        <div style="font-size:13px; color:#505a5f; display:flex; gap:12px; align-items:center;">
          <span><strong>${{mappedFns.length}}</strong> Mapped ESD Functions</span>
          <span>•</span>
          <span><strong>${{totalSvcs}}</strong> Linked Services</span>
        </div>
      </div>

      <!-- Add Function Autocomplete Bar -->
      <div class="function-search-container" style="margin-bottom: 24px;">
        <label class="govuk-label govuk-!-font-weight-bold" for="map-function-input" style="font-size:14px;">
          + Map ESD Function to ${{domain.name}}
        </label>
        <div style="display:flex; gap:8px;">
          <input type="text" 
                 id="map-function-input" 
                 class="govuk-input" 
                 placeholder="Search 176 ESD functions by name or ID (e.g. Planning, Highways, 148)..." 
                 autocomplete="off"
                 oninput="WorkbenchApp.onFunctionSearchInput(this.value)"
                 onkeydown="WorkbenchApp.onFunctionSearchKeydown(event)"
                 onfocus="WorkbenchApp.onFunctionSearchInput(this.value)">
        </div>
        <div class="function-autocomplete-menu" id="function-autocomplete-menu">
          <!-- Autocomplete results injected here -->
        </div>
      </div>
      
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h2 class="govuk-heading-m govuk-!-margin-bottom-0">Mapped ESD Functions (${{mappedFns.length}})</h2>
        <a href="#" class="govuk-link" style="font-size:14px;" onclick="WorkbenchApp.toggleAllServices(event)">Toggle All Services</a>
      </div>
    `;

    if (mappedFns.length === 0) {{
      html += `<p class="govuk-body" style="color:#505a5f; font-style:italic; margin-top:20px;">No functions mapped to this domain.</p>`;
    }} else {{
      html += `<div class="mapped-functions-list" style="display:flex; flex-direction:column; gap:16px;">`;
      mappedFns.forEach(fn => {{
        const svcs = fn.services || [];
        const fnName = fn.name || fn.label || (typeof ESD_FUNCTIONS_DB !== 'undefined' && ESD_FUNCTIONS_DB[fn.function_id] ? ESD_FUNCTIONS_DB[fn.function_id].name : undefined) || "Unknown";
        // Check cross-mapping
        const mappedDomains = inverseMap[fn.function_id] || [];
        const crossMapTags = mappedDomains
            .filter(md => md.id !== state.currentDomainId)
            .map(md => `<span class="govuk-tag govuk-tag--grey" style="font-size:11px; margin-right:4px;">Also: ${{md.name}}</span>`)
            .join('');

        html += `
          <div class="mapped-function-card" style="display:flex; border:1px solid #b1b4b6; border-left:4px solid #1d70b8; background:#fff; position:relative;">
            
            <!-- Left Info Column -->
            <div style="flex:1; padding:16px;">
              <div style="font-size:18px; font-weight:bold; margin-bottom:8px; display:flex; align-items:center; flex-wrap:wrap; gap:8px;">
                ${{fnName}}
                ${{crossMapTags}}
              </div>
              
              <div style="font-size:14px; color:#505a5f; margin-bottom:12px; display:flex; gap:12px; align-items:center;">
                <span style="font-weight:bold; color:#1d70b8;">[ESD-${{fn.function_id}}]</span>
                <span>•</span>
                <span>${{svcs.length}} Child Services</span>
                <span>•</span>
                <a href="${{fn.uri}}" target="_blank" class="govuk-link">ESD Standard ↗</a>
              </div>
              
              <button class="govuk-accordion__show-all" style="background:none; border:none; color:#1d70b8; cursor:pointer; text-decoration:underline; font-size:14px; padding:0; display:flex; align-items:center; gap:4px;"
                      onclick="WorkbenchApp.toggleServicesList(${{fn.function_id}})">
                <span id="svc-toggle-icon-${{fn.function_id}}">▶</span> Show ${{svcs.length}} Child Services
              </button>
              
              <div id="svc-list-${{fn.function_id}}" style="display:none; margin-top:12px; border-top:1px dashed #b1b4b6; padding-top:12px;">
                ${{svcs.length > 0 
                  ? svcs.map(s => `<span class="govuk-tag govuk-tag--grey child-service-tag">[${{s.identifier}}] ${{s.label}}</span>`).join(' ')
                  : '<span class="govuk-hint" style="font-size:14px;">No nested statutory services.</span>'
                }}
              </div>
            </div>

            <!-- Right Action Column -->
            <div style="width:180px; background:#f3f2f1; border-left:1px solid #d8d8d8; padding:16px; display:flex; flex-direction:column; gap:12px; justify-content:flex-start;">
              <button class="govuk-button govuk-button--secondary" style="margin-bottom:0; width:100%;" onclick="WorkbenchApp.inspectFunction(${{fn.function_id}}, '${{fnName.replace(/'/g, "\\\\'")}}')">
                Inspect
              </button>
              <button class="govuk-button" style="margin-bottom:0; width:100%;" onclick="WorkbenchApp.openMappingModal(${{fn.function_id}}, '${{fnName.replace(/'/g, "\\\\'")}}')">
                Edit Mapping
              </button>
            </div>
            
          </div>
        `;
      }});
      html += `</div>`;
    }}

    container.innerHTML = html;
  }}


  let modalActiveFunctionId = null;

  function openMappingModal(funcId, funcName) {{
    modalActiveFunctionId = funcId;
    const modal = document.getElementById("edit-mapping-modal");
    document.getElementById("modal-function-title").innerText = `[ESD-${{funcId}}] ${{funcName}}`;
    
    // Populate select
    const select = document.getElementById("modal-domain-select");
    let optionsHtml = '';
    
    // Group domains by type
    const baDomains = Object.values(state.workingMapping).filter(d => d.type === "BusinessArea").sort((a,b) => a.name.localeCompare(b.name));
    const caDomains = Object.values(state.workingMapping).filter(d => d.type === "CorporateArea").sort((a,b) => a.name.localeCompare(b.name));
    
    optionsHtml += `<optgroup label="Business Areas">`;
    baDomains.forEach(d => {{
      const selected = (d.domain_id === state.currentDomainId) ? 'selected' : '';
      optionsHtml += `<option value="${{d.domain_id}}" ${{selected}}>${{d.name}}</option>`;
    }});
    optionsHtml += `</optgroup><optgroup label="Corporate Areas">`;
    caDomains.forEach(d => {{
      const selected = (d.domain_id === state.currentDomainId) ? 'selected' : '';
      optionsHtml += `<option value="${{d.domain_id}}" ${{selected}}>${{d.name}}</option>`;
    }});
    optionsHtml += `</optgroup>`;
    
    select.innerHTML = optionsHtml;
    
    // Populate rationale
    const rationale = state.functionNotes[funcId] || "";
    document.getElementById("modal-rationale-textarea").value = rationale;
    
    modal.style.display = "flex";
  }}

  function closeMappingModal() {{
    document.getElementById("edit-mapping-modal").style.display = "none";
    modalActiveFunctionId = null;
  }}

  function saveMappingModal() {{
    if (!modalActiveFunctionId) return;
    
    const funcId = modalActiveFunctionId;
    const newDomainId = document.getElementById("modal-domain-select").value;
    const rationale = document.getElementById("modal-rationale-textarea").value;
    
    // Save rationale
    state.functionNotes[funcId] = rationale;
    saveToLocalStorage();
    
    // Handle Remap if domain changed
    if (newDomainId !== state.currentDomainId) {{
       const currentDomain = state.workingMapping[state.currentDomainId];
       const newDomain = state.workingMapping[newDomainId];
       
       const fnIndex = currentDomain.functions.findIndex(f => f.function_id === funcId);
       if (fnIndex !== -1) {{
           const fnObj = currentDomain.functions.splice(fnIndex, 1)[0];
           if (!newDomain.functions) newDomain.functions = [];
           // ensure no dupe
           if (!newDomain.functions.some(f => f.function_id === funcId)) {{
               newDomain.functions.push(fnObj);
           }}
           state.modifiedDomains.add(state.currentDomainId);
           state.modifiedDomains.add(newDomainId);
       }}
    }} else {{
       // Just saving notes counts as modification to domain conceptually
       state.modifiedDomains.add(state.currentDomainId);
    }}
    
    saveToLocalStorage();
    renderDomainList();
    renderWorkbenchCentre();
    closeMappingModal();
    showToast("Mapping saved successfully", "success");
  }}

  function unmapFromModal() {{
    if (!modalActiveFunctionId) return;
    const funcId = modalActiveFunctionId;
    
    if (!confirm(`Are you sure you want to unmap this function from LGAM?`)) {{
      return;
    }}
    
    const domain = state.workingMapping[state.currentDomainId];
    const idx = domain.functions.findIndex(f => f.function_id === funcId);
    if (idx !== -1) {{
      domain.functions.splice(idx, 1);
      state.modifiedDomains.add(state.currentDomainId);
      saveToLocalStorage();
      renderDomainList();
      renderWorkbenchCentre();
      closeMappingModal();
      showToast("Function unmapped", "info");
    }}
  }}



  // AUTOCOMPLETE SEARCH LOGIC
  function onFunctionSearchInput(query) {{
    const menu = document.getElementById("function-autocomplete-menu");
    if (!menu) return;

    query = (query || "").trim().toLowerCase();
    if (!query) {{
      menu.classList.remove("is-open");
      menu.innerHTML = "";
      return;
    }}

    const currentDomain = state.workingMapping[state.currentDomainId];
    const alreadyMappedIds = new Set((currentDomain.functions || []).map(f => String(f.function_id)));

    // Search across 176 ESD functions
    const results = [];
    for (const fId in ESD_HIERARCHY) {{
      const fn = ESD_HIERARCHY[fId];
      const matchLabel = fn.label.toLowerCase().includes(query);
      const matchId = String(fn.identifier).includes(query);
      const matchDesc = (fn.description || "").toLowerCase().includes(query);
      const matchParent = (fn.parents || []).some(p => p.label.toLowerCase().includes(query));

      if (matchLabel || matchId || matchDesc || matchParent) {{
        results.push(fn);
      }}
      if (results.length >= 25) break;
    }}

    if (results.length === 0) {{
      menu.innerHTML = `
        <div style="padding:12px; font-size:13px; color:#505a5f; text-align:center;">
          No matching ESD functions found for "${{query}}"
        </div>
      `;
      menu.classList.add("is-open");
      return;
    }}

    let html = "";
    results.forEach((fn, idx) => {{
      const isAlready = alreadyMappedIds.has(String(fn.identifier));
      const parentLabel = (fn.parents && fn.parents[0]) ? fn.parents[0].label : "Top-level Function";
      const svcsCount = (fn.services || []).length;

      html += `
        <div class="autocomplete-item ${{idx === state.focusedAutocompleteIndex ? 'is-focused' : ''}}" 
             onclick="WorkbenchApp.onSelectAutocompleteFunction('${{fn.identifier}}')">
          <div>
            <div style="font-weight:700;">${{fn.label}} <span style="font-family:monospace; font-weight:normal; font-size:12px;">[ESD-${{fn.identifier}}]</span></div>
            <div class="autocomplete-sub">Parent: ${{parentLabel}} • ${{svcsCount}} Services</div>
          </div>
          <div>
            ${{isAlready ? `
              <span class="domain-status-tag domain-status-tag--unmapped" style="font-size:11px;">Already Mapped</span>
            ` : `
              <button class="btn-action-small btn-action-small--inspect" style="font-size:11px;">+ Map</button>
            `}}
          </div>
        </div>
      `;
    }});

    menu.innerHTML = html;
    menu.classList.add("is-open");
  }}

  function onFunctionSearchKeydown(e) {{
    const menu = document.getElementById("function-autocomplete-menu");
    if (!menu || !menu.classList.contains("is-open")) return;

    const items = menu.querySelectorAll(".autocomplete-item");
    if (items.length === 0) return;

    if (e.key === "ArrowDown") {{
      e.preventDefault();
      state.focusedAutocompleteIndex = Math.min(state.focusedAutocompleteIndex + 1, items.length - 1);
      updateAutocompleteFocus(items);
    }} else if (e.key === "ArrowUp") {{
      e.preventDefault();
      state.focusedAutocompleteIndex = Math.max(state.focusedAutocompleteIndex - 1, 0);
      updateAutocompleteFocus(items);
    }} else if (e.key === "Enter") {{
      e.preventDefault();
      if (state.focusedAutocompleteIndex >= 0 && items[state.focusedAutocompleteIndex]) {{
        items[state.focusedAutocompleteIndex].click();
      }}
    }} else if (e.key === "Escape") {{
      menu.classList.remove("is-open");
      state.focusedAutocompleteIndex = -1;
    }}
  }}

  function updateAutocompleteFocus(items) {{
    items.forEach((it, idx) => {{
      if (idx === state.focusedAutocompleteIndex) {{
        it.classList.add("is-focused");
        it.scrollIntoView({{ block: "nearest" }});
      }} else {{
        it.classList.remove("is-focused");
      }}
    }});
  }}

  function mapFunction(fId) {{
    const domain = state.workingMapping[state.currentDomainId];
    if (!domain) return;

    const fn = ESD_HIERARCHY[String(fId)];
    if (!fn) return;

    domain.functions = domain.functions || [];
    if (domain.functions.some(f => String(f.function_id) === String(fId))) {{
      showToast(`Function "${{fn.label}}" is already mapped in ${{domain.name}}`, "warning");
      return;
    }}

    // Add function with its services
    domain.functions.push({{
      function_id: String(fn.identifier),
      label: fn.label,
      uri: fn.uri,
      services_count: (fn.services || []).length,
      services: (fn.services || []).map(s => ({{
        identifier: s.identifier,
        label: s.label,
        uri: s.uri
      }}))
    }});

    // Update domain stats
    domain.functions_count = domain.functions.length;
    domain.total_services_count = domain.functions.reduce((acc, f) => acc + (f.services ? f.services.length : 0), 0);

    state.inspectedFunctionId = String(fId);
    saveToLocalStorage();
    renderWorkbenchCentre();
    renderInspector();
    updateGlobalCounters();
    updateDiffMetrics();
    renderDomainList();
    updateDraftStatusBanner();

    // Close autocomplete
    const menu = document.getElementById("function-autocomplete-menu");
    const input = document.getElementById("map-function-input");
    if (menu) menu.classList.remove("is-open");
    if (input) input.value = "";

    showToast(`Mapped [ESD-${{fId}}] ${{fn.label}} to ${{domain.name}}`, "success");
  }}

  function unmapFunction(fId) {{
    const domain = state.workingMapping[state.currentDomainId];
    if (!domain || !domain.functions) return;

    const fnObj = domain.functions.find(f => String(f.function_id) === String(fId));
    const fnLabel = fnObj ? fnObj.label : fId;

    domain.functions = domain.functions.filter(f => String(f.function_id) !== String(fId));
    domain.functions_count = domain.functions.length;
    domain.total_services_count = domain.functions.reduce((acc, f) => acc + (f.services ? f.services.length : 0), 0);

    saveToLocalStorage();
    renderWorkbenchCentre();
    renderInspector();
    updateGlobalCounters();
    updateDiffMetrics();
    renderDomainList();
    updateDraftStatusBanner();

    showToast(`Unmapped [ESD-${{fId}}] ${{fnLabel}} from ${{domain.name}}`, "info");
  }}

  // RIGHT PANE: REFERENCE INSPECTOR RENDER
  function renderInspector() {{
    const container = document.getElementById("inspector-body-container");
    if (!container) return;

    const fn = ESD_HIERARCHY[String(state.inspectedFunctionId)];
    if (!fn) {{
      container.innerHTML = `
        <div style="background:#f8f8f8; border:1px solid #d8d8d8; border-radius:4px; padding:24px; text-align:center; color:#505a5f;">
          <h3 class="govuk-heading-s">No Function Selected</h3>
          <p class="govuk-body-s">Click <strong>🔍 Inspect</strong> on any function card in the workbench to inspect its official statutory duties, hierarchy, and definition.</p>
        </div>
      `;
      return;
    }}

    // Compute hierarchy breadcrumb
    const parentTrail = [];
    if (fn.parents && fn.parents.length > 0) {{
      fn.parents.forEach(p => {{
        parentTrail.push(p.label);
      }});
    }}

    // Filter matching Powers and Duties
    const matchingPD = filterPowersDutiesForFunction(fn);

    let html = `
      <div style="border-bottom:2px solid #1d70b8; padding-bottom:12px; margin-bottom:16px;">
        <span class="domain-type-badge domain-type-badge--ba" style="font-size:11px;">ESD Function Definition</span>
        <h3 class="govuk-heading-m govuk-!-margin-top-1 govuk-!-margin-bottom-1">${{fn.label}}</h3>
        <div style="font-size:12px; color:#505a5f; display:flex; gap:8px; align-items:center;">
          <span style="font-family:monospace; font-weight:700; color:#1d70b8;">[ESD-${{fn.identifier}}]</span>
          <span>•</span>
          <a href="${{fn.uri}}" target="_blank" rel="noopener noreferrer" class="govuk-link">Official ESD Standard URI ↗</a>
        </div>
      </div>

      <!-- Description Box -->
      <div class="inspector-detail-box">
        <span class="inspector-detail-label">Official Function Description</span>
        <div class="inspector-detail-value">
          ${{fn.description ? fn.description : '<em style="color:#505a5f;">No descriptive summary registered in ESD definition.</em>'}}
        </div>
      </div>

      <!-- Hierarchy Trail -->
      <div class="inspector-detail-box">
        <span class="inspector-detail-label">Taxonomy Hierarchy Lineage</span>
        <div class="hierarchy-trail">
          <span class="hierarchy-step">LGA Root</span>
          <span class="hierarchy-sep">&gt;</span>
          ${{parentTrail.length > 0 ? parentTrail.map(p => `
            <span class="hierarchy-step">${{p}}</span>
            <span class="hierarchy-sep">&gt;</span>
          `).join('') : ''}}
          <span class="hierarchy-step" style="background:#1d70b8; color:#fff; border-color:#1d70b8;">${{fn.label}}</span>
        </div>
      </div>

      <!-- Child Services -->
      <div class="inspector-detail-box">
        <span class="inspector-detail-label">Child Statutory Services (${{(fn.services || []).length}})</span>
        ${{(fn.services || []).length === 0 ? `
          <div style="font-size:12px; color:#505a5f;">No discrete services defined under this function.</div>
        ` : `
          <div class="service-chip-list" style="margin-top:6px;">
            ${{fn.services.map(s => `
              <span class="service-chip">
                <span class="service-chip-id">[${{s.identifier}}]</span>
                <span>${{s.label}}</span>
              </span>
            `).join('')}}
          </div>
        `}}
      </div>

      <!-- Statutory Powers & Duties -->
      <div style="margin-top:20px;">
        <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;">
          <h4 class="govuk-heading-s govuk-!-margin-bottom-0">
            Statutory Powers &amp; Duties (<span id="pd-match-count">${{matchingPD.length}}</span>)
          </h4>
          <span style="font-size:11px; color:#505a5f;">From 4,025 legal records</span>
        </div>

        <div class="pd-search-box">
          <input type="search" 
                 id="pd-search-input" 
                 class="govuk-input" 
                 style="font-size:13px; padding:4px 8px;" 
                 placeholder="Search legislation / duties (e.g. Care Act, Section 106, penalty)..."
                 value="${{state.pdSearchTerm}}"
                 oninput="WorkbenchApp.onPDSearchInput(this.value)">
        </div>

        <div class="pd-type-filters">
          <button class="pd-type-pill ${{state.pdFilterType === 'all' ? 'is-selected' : ''}}" onclick="WorkbenchApp.setPDFilter('all')">All</button>
          <button class="pd-type-pill ${{state.pdFilterType === 'duty' ? 'is-selected' : ''}}" onclick="WorkbenchApp.setPDFilter('duty')">Duties (Mandatory)</button>
          <button class="pd-type-pill ${{state.pdFilterType === 'power' ? 'is-selected' : ''}}" onclick="WorkbenchApp.setPDFilter('power')">Powers (Discretionary)</button>
        </div>

        <div class="pd-list-container" id="pd-list-container">
          <!-- Populated by matchingPD -->
        </div>
      </div>
    `;

    container.innerHTML = html;
    renderPDList(matchingPD);
  }}

  function filterPowersDutiesForFunction(fn) {{
    const fnLabel = fn.label.toLowerCase();
    const svcLabels = (fn.services || []).map(s => s.label.toLowerCase());

    // Extract significant keywords
    const keywords = new Set();
    fnLabel.split(/[^a-zA-Z0-9]+/).forEach(w => {{
      if (w.length >= 4 && !['service','services','council','local','authority','public','provision','support','management','general'].includes(w)) {{
        keywords.add(w);
      }}
    }});
    svcLabels.forEach(sl => {{
      sl.split(/[^a-zA-Z0-9]+/).forEach(w => {{
        if (w.length >= 4 && !['service','services','council','local','authority','public','provision','support','management','general'].includes(w)) {{
          keywords.add(w);
        }}
      }});
    }});

    const searchFilter = (state.pdSearchTerm || "").toLowerCase().trim();
    const typeFilter = state.pdFilterType;

    const matches = [];

    for (let i = 0; i < ESD_POWERS_DUTIES.length; i++) {{
      const item = ESD_POWERS_DUTIES[i];

      // Type filter
      if (typeFilter !== "all" && item.type !== typeFilter) continue;

      const itemLabel = item.label.toLowerCase();
      const itemDesc = (item.desc || "").toLowerCase();

      // If user typed a search filter, match that explicitly
      if (searchFilter) {{
        if (itemLabel.includes(searchFilter) || itemDesc.includes(searchFilter) || String(item.id).includes(searchFilter)) {{
          matches.push(item);
        }}
        continue;
      }}

      // Smart matching by function & services
      if (itemLabel.includes(fnLabel)) {{
        matches.push(item);
        continue;
      }}

      const matchedSvc = svcLabels.some(sl => sl.length > 4 && itemLabel.includes(sl));
      if (matchedSvc) {{
        matches.push(item);
        continue;
      }}

      let score = 0;
      keywords.forEach(kw => {{
        if (itemLabel.includes(kw)) score += 2;
        else if (itemDesc.includes(kw)) score += 1;
      }});

      if (score >= 3) {{
        matches.push(item);
      }}
    }}

    return matches;
  }}

  function renderPDList(items) {{
    const container = document.getElementById("pd-list-container");
    if (!container) return;

    if (items.length === 0) {{
      container.innerHTML = `
        <div style="background:#f8f8f8; border:1px dashed #b1b4b6; padding:16px; font-size:12px; color:#505a5f; text-align:center; border-radius:3px;">
          No statutory powers or duties found matching criteria. Use the search input above to search all 4,025 records.
        </div>
      `;
      return;
    }}

    // Limit to top 50 for performance
    const displayItems = items.slice(0, 50);
    let html = "";
    displayItems.forEach(item => {{
      const isDuty = item.type === "duty";
      html += `
        <div class="pd-card ${{isDuty ? '' : 'pd-card--power'}}">
          <div class="pd-card-header">
            <div>
              <span class="pd-tag ${{isDuty ? 'pd-tag--duty' : 'pd-tag--power'}}">${{isDuty ? 'Duty' : 'Power'}}</span>
              <span class="pd-card-title" style="margin-left:4px;">${{item.label}}</span>
            </div>
            <span style="font-family:monospace; color:#505a5f; font-size:11px;">[#${{item.id}}]</span>
          </div>
          <div class="pd-card-desc">
            ${{item.desc ? item.desc : 'Statutory provisions conferred by parliament.'}}
          </div>
          <div style="margin-top:6px;">
            <a href="${{item.uri}}" target="_blank" rel="noopener noreferrer" class="govuk-link" style="font-size:11px;">
              View ESD Legislation Record ↗
            </a>
          </div>
        </div>
      `;
    }});

    if (items.length > 50) {{
      html += `
        <div style="font-size:11px; color:#505a5f; text-align:center; padding:6px;">
          Showing top 50 of ${{items.length}} records. Refine search to filter.
        </div>
      `;
    }}

    container.innerHTML = html;
  }}

  // EXPORT FUNCTIONS
  function generateJsonOutput() {{
    const out = {{
      metadata: {{
        source: BASELINE_MAPPING.metadata.source,
        api_base: BASELINE_MAPPING.metadata.api_base,
        description: BASELINE_MAPPING.metadata.description,
        lgam_domains_count: Object.keys(state.workingMapping).length,
        total_esd_functions: Object.keys(ESD_HIERARCHY).length,
        total_esd_services: BASELINE_MAPPING.metadata.total_esd_services,
        last_curated: new Date().toISOString()
      }},
      mappings: state.workingMapping
    }};
    return JSON.stringify(out, null, 2);
  }}

  function generateCsvOutput() {{
    const rows = [
      ["Domain ID", "Domain Name", "Domain Type", "Function ID", "Function Label", "Function URI", "Service ID", "Service Label", "Service URI", "Curator Notes"]
    ];

    for (const dId in state.workingMapping) {{
      const d = state.workingMapping[dId];
      const notes = (d.curator_notes || "").replace(/"/g, '""');

      if (!d.functions || d.functions.length === 0) {{
        rows.push([
          `"${{d.domain_id}}"`,
          `"${{d.name}}"`,
          `"${{d.type}}"`,
          '""', '""', '""', '""', '""', '""',
          `"${{notes}}"`
        ]);
        continue;
      }}

      d.functions.forEach(fn => {{
        if (!fn.services || fn.services.length === 0) {{
          rows.push([
            `"${{d.domain_id}}"`,
            `"${{d.name}}"`,
            `"${{d.type}}"`,
            `"${{fn.function_id}}"`,
            `"${{fn.label.replace(/"/g, '""')}}"`,
            `"${{fn.uri}}"`,
            '""', '""', '""',
            `"${{notes}}"`
          ]);
        }} else {{
          fn.services.forEach(s => {{
            rows.push([
              `"${{d.domain_id}}"`,
              `"${{d.name}}"`,
              `"${{d.type}}"`,
              `"${{fn.function_id}}"`,
              `"${{fn.label.replace(/"/g, '""')}}"`,
              `"${{fn.uri}}"`,
              `"${{s.identifier}}"`,
              `"${{s.label.replace(/"/g, '""')}}"`,
              `"${{s.uri}}"`,
              `"${{notes}}"`
            ]);
          }});
        }}
      }});
    }}

    return rows.map(r => r.join(",")).join("\\r\\n");
  }}

  function triggerDownload(content, filename, mimeType) {{
    const blob = new Blob([content], {{ type: mimeType }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${{filename}}`, "success");
  }}

  // Public API exposed to window.WorkbenchApp
  window.WorkbenchApp = {{
    openMappingModal: openMappingModal,
    closeMappingModal: closeMappingModal,
    saveMappingModal: saveMappingModal,
    unmapFromModal: unmapFromModal,
    init: function() {{
      initDraftPersistence();
      renderDomainList();
      renderWorkbenchCentre();
      renderInspector();
      updateGlobalCounters();
      updateDraftStatusBanner();
      updateDiffMetrics();
    }},

    selectDomain: function(dId) {{
      state.currentDomainId = dId;
      state.focusedAutocompleteIndex = -1;
      renderDomainList();
      renderWorkbenchCentre();
    }},

    inspectFunction: function(fId) {{
      state.inspectedFunctionId = String(fId);
      state.activeTab = "inspector";
      renderWorkbenchCentre();
      renderInspector();
      this.switchTab("inspector");
    }},

    switchTab: function(tabName) {{
      state.activeTab = tabName;
      const btnInspector = document.getElementById("tab-btn-inspector");
      const btnExport = document.getElementById("tab-btn-export");
      const contentInspector = document.getElementById("tab-content-inspector");
      const contentExport = document.getElementById("tab-content-export");

      if (tabName === "inspector") {{
        if (btnInspector) {{ btnInspector.classList.add("is-active"); btnInspector.setAttribute("aria-selected", "true"); }}
        if (btnExport) {{ btnExport.classList.remove("is-active"); btnExport.setAttribute("aria-selected", "false"); }}
        if (contentInspector) contentInspector.classList.add("is-active");
        if (contentExport) contentExport.classList.remove("is-active");
      }} else {{
        if (btnExport) {{ btnExport.classList.add("is-active"); btnExport.setAttribute("aria-selected", "true"); }}
        if (btnInspector) {{ btnInspector.classList.remove("is-active"); btnInspector.setAttribute("aria-selected", "false"); }}
        if (contentExport) contentExport.classList.add("is-active");
        if (contentInspector) contentInspector.classList.remove("is-active");
        updateDiffMetrics();
      }}
    }},

    onDomainSearch: function(query) {{
      state.domainSearchTerm = query;
      renderDomainList();
    }},

    setDomainFilter: function(filter) {{
      state.domainCategoryFilter = filter;
      document.querySelectorAll(".domain-filter-pill").forEach(p => {{
        if (p.getAttribute("data-filter") === filter) {{
          p.classList.add("is-selected");
        }} else {{
          p.classList.remove("is-selected");
        }}
      }});
      renderDomainList();
    }},

    onNotesInput: function(val) {{
      const domain = state.workingMapping[state.currentDomainId];
      if (domain) {{
        domain.curator_notes = val;
        saveToLocalStorage();
      }}
    }},

    onFunctionSearchInput: onFunctionSearchInput,
    onFunctionSearchKeydown: onFunctionSearchKeydown,
    onSelectAutocompleteFunction: function(fId) {{
      mapFunction(fId);
    }},

    unmapFunction: unmapFunction,

    toggleServices: function(fId) {{
      state.expandedServices[fId] = !state.expandedServices[fId];
      renderWorkbenchCentre();
    }},

    toggleAllServices: function() {{
      const domain = state.workingMapping[state.currentDomainId];
      if (!domain || !domain.functions) return;
      const anyExpanded = domain.functions.some(f => state.expandedServices[f.function_id]);
      domain.functions.forEach(f => {{
        state.expandedServices[f.function_id] = !anyExpanded;
      }});
      renderWorkbenchCentre();
    }},

    onPDSearchInput: function(val) {{
      state.pdSearchTerm = val;
      const fn = ESD_HIERARCHY[String(state.inspectedFunctionId)];
      if (fn) {{
        const matching = filterPowersDutiesForFunction(fn);
        const countSpan = document.getElementById("pd-match-count");
        if (countSpan) countSpan.textContent = matching.length;
        renderPDList(matching);
      }}
    }},

    setPDFilter: function(type) {{
      state.pdFilterType = type;
      document.querySelectorAll(".pd-type-pill").forEach(p => {{
        p.classList.remove("is-selected");
      }});
      const target = document.querySelector(`.pd-type-pill[onclick*="'${{type}}'"]`);
      if (target) target.classList.add("is-selected");

      const fn = ESD_HIERARCHY[String(state.inspectedFunctionId)];
      if (fn) {{
        const matching = filterPowersDutiesForFunction(fn);
        const countSpan = document.getElementById("pd-match-count");
        if (countSpan) countSpan.textContent = matching.length;
        renderPDList(matching);
      }}
    }},

    downloadJson: function() {{
      const content = generateJsonOutput();
      triggerDownload(content, "lgam-to-esd-mapping.json", "application/json");
    }},

    downloadCsv: function() {{
      const content = generateCsvOutput();
      triggerDownload(content, "lgam-esd-taxonomy-mapping.csv", "text/csv;charset=utf-8;");
    }},

    copyJsonToClipboard: function() {{
      const content = generateJsonOutput();
      if (navigator.clipboard) {{
        navigator.clipboard.writeText(content).then(() => {{
          showToast("Copied full JSON mapping to clipboard!", "success");
        }}).catch(() => {{
          showToast("Failed to copy automatically. Use Download JSON.", "warning");
        }});
      }} else {{
        showToast("Clipboard API unavailable in this context.", "warning");
      }}
    }},

    promptResetBaseline: function() {{
      if (confirm("Reset all curation changes and revert to the official baseline mapping? This will erase your unexported local draft.")) {{
        this.discardDraft();
      }}
    }},

    discardDraft: function() {{
      try {{
        localStorage.removeItem(STORAGE_KEY);
        state.workingMapping = JSON.parse(JSON.stringify(BASELINE_MAPPING.mappings));
        state.hasDraftSaved = false;
        const banner = document.getElementById("draft-recovery-banner");
        if (banner) banner.classList.remove("is-active");
        renderDomainList();
        renderWorkbenchCentre();
        renderInspector();
        updateGlobalCounters();
        updateDraftStatusBanner();
        updateDiffMetrics();
        showToast("Restored baseline taxonomy mapping.", "info");
      }} catch (e) {{
        console.error("Discard draft error:", e);
      }}
    }},

    openUnmappedPoolModal: function() {{
      const modal = document.getElementById("unmapped-pool-modal");
      const list = document.getElementById("unmapped-functions-list");
      const curDomainLabel = document.getElementById("modal-current-domain-name");
      const curDomain = state.workingMapping[state.currentDomainId];

      if (curDomainLabel && curDomain) {{
        curDomainLabel.textContent = curDomain.name;
      }}

      const unmapped = getUnmappedFunctions();
      if (list) {{
        if (unmapped.length === 0) {{
          list.innerHTML = `
            <div style="background:#cce2d8; padding:16px; border-radius:4px; color:#005a30; font-size:13px; font-weight:700; text-align:center;">
              ✓ Complete Coverage: All 176 ESD functions are currently mapped across LGAM domains!
            </div>
          `;
        }} else {{
          let html = "";
          unmapped.forEach(fn => {{
            const svcsCount = (fn.services || []).length;
            const parentLabel = (fn.parents && fn.parents[0]) ? fn.parents[0].label : "Top-level";
            html += `
              <div style="background:#f8f8f8; border:1px solid #d8d8d8; padding:10px 14px; border-radius:4px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <strong style="font-size:14px; color:#0b0c0c;">${{fn.label}}</strong>
                  <span style="font-family:monospace; font-size:12px; color:#505a5f; margin-left:4px;">[ESD-${{fn.identifier}}]</span>
                  <div style="font-size:12px; color:#505a5f; margin-top:2px;">Parent: ${{parentLabel}} • ${{svcsCount}} Services</div>
                </div>
                <button class="btn-action-small btn-action-small--inspect" onclick="WorkbenchApp.mapFromModal('${{fn.identifier}}')">
                  + Map to ${{curDomain ? curDomain.name : 'Domain'}}
                </button>
              </div>
            `;
          }});
          list.innerHTML = html;
        }}
      }}

      if (modal) modal.classList.add("is-active");
    }},

    mapFromModal: function(fId) {{
      mapFunction(fId);
      this.openUnmappedPoolModal(); // Re-render modal list
    }},

    closeUnmappedPoolModal: function() {{
      const modal = document.getElementById("unmapped-pool-modal");
      if (modal) modal.classList.remove("is-active");
    }}
  }};

  // Initialize on DOM ready
  document.addEventListener("DOMContentLoaded", function() {{
    window.WorkbenchApp.init();
  }});

  // Close modals on Escape key
  document.addEventListener("keydown", function(e) {{
    if (e.key === "Escape") {{
      window.WorkbenchApp.closeUnmappedPoolModal();
    }}
  }});
}})();
</page-script>
'''

    os.makedirs(os.path.dirname(OUTPUT_PAGE), exist_ok=True)
    with open(OUTPUT_PAGE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Successfully generated: {OUTPUT_PAGE} ({len(html_content)} bytes)")

if __name__ == "__main__":
    build_workbench_page()
