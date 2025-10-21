import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

// 마인드맵 데이터 노드의 타입 정의
interface MindMapNode {
  name: string;
  children?: MindMapNode[];
}

interface Props {
  mindmapData: MindMapNode;
}

// JSON 데이터를 Mermaid 구문으로 변환하는 재귀 함수
const jsonToMermaidSyntax = (node: MindMapNode, parentId: string, idCounter: { val: number }): string => {
  let syntax = '';
  if (!node || !node.name) return '';

  idCounter.val++;
  const currentNodeId = `node${idCounter.val}`;
  // Mermaid는 노드 ID에 특수문자를 허용하지 않으므로 간단한 ID를 사용합니다.
  // 실제 텍스트는 노드 레이블에 표시합니다.
  syntax += `    ${parentId} --> ${currentNodeId}["${node.name.replace(/