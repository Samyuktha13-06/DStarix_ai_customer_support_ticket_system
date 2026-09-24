import React from "react";

function formatInline(text) {
  if (!text) return null;

  // Match:
  // 1: `code`
  // 2: **bold** or __bold__
  // 3: *italic* or _italic_
  // 4: [link text](url)
  const regex = /(`[^`]+`)|(\*\*[^*]+\*\*)|(__[^_]+__)|(\*[^*]+\*)|(_[^_]+_)|(\[[^\]]+\]\([^)]+\))/g;

  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    const token = match[0];
    const key = `inline-${match.index}`;

    if (token.startsWith("`") && token.endsWith("`")) {
      parts.push(<code key={key}>{token.slice(1, -1)}</code>);
    } else if (
      (token.startsWith("**") && token.endsWith("**")) ||
      (token.startsWith("__") && token.endsWith("__"))
    ) {
      parts.push(<strong key={key}>{token.slice(2, -2)}</strong>);
    } else if (
      (token.startsWith("*") && token.endsWith("*")) ||
      (token.startsWith("_") && token.endsWith("_"))
    ) {
      parts.push(<em key={key}>{token.slice(1, -1)}</em>);
    } else if (token.startsWith("[") && token.includes("](")) {
      const linkMatch = token.match(/\[([^\]]+)\]\(([^)]+)\)/);
      if (linkMatch) {
        parts.push(
          <a
            key={key}
            href={linkMatch[2]}
            target="_blank"
            rel="noopener noreferrer"
          >
            {linkMatch[1]}
          </a>
        );
      } else {
        parts.push(token);
      }
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts;
}

export default function MarkdownText({ content }) {
  if (!content) return null;

  const lines = content.split("\n");
  const elements = [];
  let currentList = null;
  let currentListType = null;
  let paragraphLines = [];

  const flushParagraph = () => {
    if (paragraphLines.length > 0) {
      const text = paragraphLines.join(" ");
      if (text.trim()) {
        elements.push(
          <p key={`p-${elements.length}`} className="markdown-p">
            {formatInline(text)}
          </p>
        );
      }
      paragraphLines = [];
    }
  };

  const flushList = () => {
    if (currentList && currentList.length > 0) {
      if (currentListType === "ol") {
        elements.push(
          <ol key={`ol-${elements.length}`} className="markdown-list">
            {currentList.map((item, idx) => (
              <li
                key={idx}
                className={item.isNested ? "nested-item" : ""}
                style={item.isNested ? { marginLeft: "18px", listStyleType: "circle" } : {}}
              >
                {formatInline(item.text)}
              </li>
            ))}
          </ol>
        );
      } else {
        elements.push(
          <ul key={`ul-${elements.length}`} className="markdown-list">
            {currentList.map((item, idx) => (
              <li
                key={idx}
                className={item.isNested ? "nested-item" : ""}
                style={item.isNested ? { marginLeft: "18px", listStyleType: "circle" } : {}}
              >
                {formatInline(item.text)}
              </li>
            ))}
          </ul>
        );
      }
      currentList = null;
      currentListType = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const isIndented = rawLine.startsWith("  ") || rawLine.startsWith("\t");
    const trimmed = rawLine.trim();

    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    // Unordered list: "- ..." or "* ..."
    const ulMatch = trimmed.match(/^[-*]\s+(.*)$/);
    if (ulMatch) {
      flushParagraph();
      if (currentListType && currentListType !== "ul") {
        flushList();
      }
      if (!currentList) {
        currentList = [];
        currentListType = "ul";
      }
      currentList.push({
        text: ulMatch[1],
        isNested: isIndented,
      });
      continue;
    }

    // Ordered list: "1. ..."
    const olMatch = trimmed.match(/^\d+\.\s+(.*)$/);
    if (olMatch) {
      flushParagraph();
      if (currentListType && currentListType !== "ol") {
        flushList();
      }
      if (!currentList) {
        currentList = [];
        currentListType = "ol";
      }
      currentList.push({
        text: olMatch[1],
        isNested: isIndented,
      });
      continue;
    }

    // Headings: "# ...", "## ...", "### ..."
    const headingMatch = trimmed.match(/^(#{1,3})\s+(.*)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      const level = headingMatch[1].length;
      const text = headingMatch[2];
      if (level === 1) {
        elements.push(<h3 key={`h-${elements.length}`} className="markdown-h3">{formatInline(text)}</h3>);
      } else if (level === 2) {
        elements.push(<h4 key={`h-${elements.length}`} className="markdown-h4">{formatInline(text)}</h4>);
      } else {
        elements.push(<h5 key={`h-${elements.length}`} className="markdown-h5">{formatInline(text)}</h5>);
      }
      continue;
    }

    // Regular line in paragraph
    flushList();
    paragraphLines.push(trimmed);
  }

  flushParagraph();
  flushList();

  return <div className="markdown-container">{elements}</div>;
}
