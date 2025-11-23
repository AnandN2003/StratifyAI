from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from src.graph import AgentState, create_research_graph
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import re

app = Flask(__name__)
CORS(app)

# Store active sessions
active_sessions = {}

@app.route('/api/research', methods=['POST'])
def research_company():
    try:
        data = request.json
        company_name = data.get('company_name')
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Initialize state
        initial_state = {
            "messages": [],
            "company_name": company_name,
            "research_data": [],
            "conflicting_info": False,
            "clarification_question": "",
            "conflicting_data": "",
            "final_report": "",
            "human_resolution": ""
        }
        
        # Create graph and run
        graph = create_research_graph()
        thread_id = f"session_{company_name}_{id(graph)}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Store in active sessions
        active_sessions[company_name] = {
            "graph": graph,
            "thread_id": thread_id,
            "config": config
        }
        
        # Run the graph - it will interrupt at human_review if conflict detected
        result_state = None
        for state in graph.stream(initial_state, config, stream_mode="values"):
            result_state = state
        
        # Check if we hit an interrupt (conflict detected)
        if result_state.get("conflicting_info"):
            return jsonify({
                'has_conflict': True,
                'conflict_question': result_state.get('clarification_question', ''),
                'conflicting_data': result_state.get('conflicting_data', ''),
                'session_id': company_name,
                'message': 'Conflict detected - human review required'
            })
        
        # No conflict - return the report
        report = result_state.get('final_report', '')
        return jsonify({
            'has_conflict': False,
            'report': report,
            'message': 'Research completed successfully'
        })
        
    except Exception as e:
        import traceback
        print("Error in research_company:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/resolve-conflict', methods=['POST'])
def resolve_conflict():
    try:
        data = request.json
        print(f"\n{'='*60}")
        print(f"🔍 RESOLVE CONFLICT REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"📦 Request data: {data}")
        
        resolution = data.get('resolution')
        session_id = data.get('session_id')
        clarification_note = data.get('clarification_note', '')
        
        print(f"✅ Resolution: {resolution}")
        print(f"✅ Session ID: {session_id}")
        print(f"✅ Clarification note: {clarification_note}")
        print(f"📋 Active sessions: {list(active_sessions.keys())}")
        print(f"{'='*60}\n")
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
            
        if session_id not in active_sessions:
            return jsonify({'error': f'Session not found. Active sessions: {list(active_sessions.keys())}'}), 400
        
        company_name = session_id
        session = active_sessions[company_name]
        graph = session['graph']
        config = session['config']
        
        # Update state with human resolution
        if resolution == 'proceed':
            updated_state = {
                "conflicting_info": False,
                "human_resolution": "proceed"
            }
        elif resolution == 'stop':
            # Clean up session
            del active_sessions[company_name]
            return jsonify({
                'status': 'stopped',
                'message': 'Research stopped by user',
                'report': '# Research Paused\n\nResearch was stopped due to conflicting information requiring manual review.'
            })
        elif resolution == 'clarify':
            updated_state = {
                "conflicting_info": False,
                "human_resolution": f"clarify: {clarification_note}"
            }
        else:
            return jsonify({'error': 'Invalid resolution type'}), 400
        
        # Continue the graph from where it paused
        print(f"🔄 Resuming graph execution...")
        print(f"📝 Updating state and resuming...")
        
        # Update the graph state at the current checkpoint
        graph.update_state(config, updated_state, as_node="human_review")
        
        # Resume execution from the updated state
        result_state = None
        for state in graph.stream(None, config, stream_mode="values"):
            result_state = state
            print(f"📊 Graph state update: conflicting_info={state.get('conflicting_info')}, has_report={bool(state.get('final_report'))}")
            if state.get('final_report'):
                print(f"✅ Report generated in stream!")
                break
        
        report = result_state.get('final_report', '')
        print(f"\n{'='*60}")
        print(f"✅ GRAPH EXECUTION COMPLETED")
        print(f"📄 Report length: {len(report)} characters")
        if report:
            print(f"📄 Report preview: {report[:150]}...")
        else:
            print(f"⚠️ WARNING: No report generated!")
        print(f"{'='*60}\n")
        
        # Clean up session
        del active_sessions[company_name]
        
        return jsonify({
            'status': 'completed',
            'message': 'Research completed with human resolution',
            'report': report
        })
        
    except Exception as e:
        import traceback
        print("Error in resolve_conflict:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    try:
        data = request.json
        content = data.get('content', '')
        company_name = data.get('company_name', 'Report')
        
        print(f"📄 PDF generation request for: {company_name}")
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=60, 
            leftMargin=60,
            topMargin=60, 
            bottomMargin=40,
            title=f"{company_name} Account Plan"
        )
        
        # Container for PDF elements
        elements = []
        
        # Define professional styles
        styles = getSampleStyleSheet()
        
        # Title style (company name)
        title_style = ParagraphStyle(
            'CompanyTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#ff4444'),
            spaceAfter=6,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Section heading style (## headers)
        section_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#ff4444'),
            borderWidth=0,
            borderPadding=0,
            leftIndent=0
        )
        
        # Subsection style (### headers)
        subsection_style = ParagraphStyle(
            'SubsectionHeading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#444444'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Body text style
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=0,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=14
        )
        
        # Bullet point style
        bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            leftIndent=20,
            fontName='Helvetica',
            leading=13
        )
        
        # Parse markdown content
        lines = content.split('\n')
        i = 0
        in_table = False
        table_data = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                if not in_table:
                    elements.append(Spacer(1, 0.15 * inch))
                i += 1
                continue
            
            # Handle main title (# header - company name)
            if line.startswith('# ') and i < 3:  # Main title at the top
                text = line.replace('# ', '').replace('Account Plan:', '').strip()
                elements.append(Paragraph(text, title_style))
                elements.append(Paragraph('Account Plan & Strategic Analysis', subtitle_style))
                elements.append(Spacer(1, 0.3 * inch))
                i += 1
                continue
            
            # Handle section headers (## )
            elif line.startswith('## '):
                text = line.replace('## ', '')
                # Add section divider line
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph(text, section_style))
                # Add underline
                elements.append(Spacer(1, 0.05 * inch))
                i += 1
                continue
            
            # Handle subsection headers (###)
            elif line.startswith('### '):
                text = line.replace('### ', '')
                elements.append(Paragraph(text, subsection_style))
                i += 1
                continue
            
            # Handle table rows
            elif line.startswith('|'):
                if not in_table:
                    in_table = True
                    table_data = []
                
                # Parse table row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                
                # Skip separator rows (----)
                if all('-' in cell for cell in cells):
                    i += 1
                    continue
                
                # Clean up cell content - remove markdown formatting
                cleaned_cells = []
                for cell in cells:
                    # Remove ** for bold
                    cell = cell.replace('**', '')
                    # Replace <br> with line breaks
                    cell = cell.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
                    # Replace - bullet points with actual bullets
                    cell = re.sub(r'^\s*-\s+', '• ', cell)
                    # Clean up multiple spaces
                    cell = re.sub(r'\s+', ' ', cell)
                    cleaned_cells.append(cell)
                
                table_data.append(cleaned_cells)
                i += 1
                
                # Check if next line is still part of table
                if i < len(lines) and not lines[i].strip().startswith('|'):
                    # End of table - render it
                    if table_data:
                        # Create table with wider columns for content
                        table = Table(table_data, colWidths=[1.5*inch, 4.5*inch])
                        table.setStyle(TableStyle([
                            # Header row styling
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff4444')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('TOPPADDING', (0, 0), (-1, 0), 12),
                            
                            # Body rows styling
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 10),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                            ('TOPPADDING', (0, 1), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                            
                            # Grid
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#ff4444')),
                            
                            # Alternating row colors
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                            
                            # Word wrap for content
                            ('WORDWRAP', (0, 0), (-1, -1), True),
                        ]))
                        elements.append(table)
                        elements.append(Spacer(1, 0.2 * inch))
                        table_data = []
                    in_table = False
                continue
            
            # Handle bold bullet points (• **text:** content)
            elif line.startswith('* **') or line.startswith('- **'):
                in_table = False
                text = line.replace('* ', '').replace('- ', '')
                # Remove ** for bold and use <b> tags
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                # Remove any remaining <br> tags
                text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
                elements.append(Paragraph(f"• {text}", bullet_style))
                i += 1
                continue
            
            # Handle regular bullet points
            elif line.startswith('* ') or line.startswith('- ') or re.match(r'^\d+\.', line):
                in_table = False
                text = re.sub(r'^[\*\-]\s+', '', line)
                text = re.sub(r'^\d+\.\s+', '', text)
                # Convert **bold** to <b>bold</b>
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                # Remove any <br> tags
                text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
                elements.append(Paragraph(f"• {text}", bullet_style))
                i += 1
                continue
            
            # Handle regular paragraphs
            else:
                in_table = False
                # Convert **bold** to <b>bold</b>
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                # Convert *italic* to <i>italic</i>
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
                # Remove any <br> tags
                text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
                elements.append(Paragraph(text, body_style))
                i += 1
                continue
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        print(f"✅ PDF generated successfully: {len(buffer.getvalue())} bytes")
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{company_name}_account_plan.pdf'
        )
        
    except Exception as e:
        import traceback
        print("Error generating PDF:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
