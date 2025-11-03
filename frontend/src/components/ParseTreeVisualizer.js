import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './ParseTreeVisualizer.css';

const ParseTreeVisualizer = ({ tree }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!tree) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const width = 800;
    const height = 400;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Convert tree to d3 hierarchy, filtering out null children
    const root = d3.hierarchy(tree, d => {
      if (!d.children) return null;
      return d.children.filter(child => child !== null && child !== undefined);
    });

    // Create tree layout
    const treeLayout = d3.tree()
      .size([width - margin.left - margin.right - 100, height - margin.top - margin.bottom - 80]);

    treeLayout(root);

    // Draw links
    svg.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d3.linkVertical()
        .x(d => d.x + 50)
        .y(d => d.y + 40))
      .attr('fill', 'none')
      .attr('stroke', '#999')
      .attr('stroke-width', 2);

    // Draw nodes
    const nodes = svg.selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.x + 50},${d.y + 40})`);

    // Add circles for nodes
    nodes.append('circle')
      .attr('r', 8)
      .attr('fill', d => {
        const label = d.data.label || '';
        if (label.includes('(plural)') && label.includes('(singular)')) {
          return '#e74c3c';  // Red for mismatch
        }
        if (label.includes('singular')) return '#3498db';  // Blue
        if (label.includes('plural')) return '#2ecc71';    // Green
        return '#95a5a6';  // Gray
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add labels
    nodes.append('text')
      .attr('dy', -12)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .text(d => d.data.label || '');

    // Add text content if present
    nodes.filter(d => d.data.text)
      .append('text')
      .attr('dy', 25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('fill', '#666')
      .attr('font-style', 'italic')
      .text(d => `"${d.data.text}"`);

  }, [tree]);

  return (
    <div className="parse-tree-container">
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default ParseTreeVisualizer;
