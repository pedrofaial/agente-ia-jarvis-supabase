import React, { useState, useEffect, useRef } from 'react';
import { useSupabase } from '../contexts/SupabaseContext';
import { useLLMConfig } from '../contexts/LLMContext';
import LLMConfiguration from './LLMConfiguration';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { 
  Cog6ToothIcon, 
  ArrowPathIcon,
  ChartBarIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ChatInterface() {
  const { user, session } = useSupabase();
  const { llmConfig, setLLMConfig } = useLLMConfig();
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showLLMConfig, setShowLLMConfig] = useState(!llmConfig);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  // Welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: '1',
        type: 'assistant',
        content: `Olá ${user?.email}! 👋\n\nSou seu assistente de gestão de obras. Posso ajudar você com:\n\n• Consultar suas obras ativas\n• Verificar custos e orçamentos\n• Gerenciar fornecedores\n• Criar relatórios financeiros\n• Analisar tendências e insights\n\nComo posso ajudar hoje?`,
        timestamp: new Date()
      }]);
    }
  }, []);

  const sendMessage = async (content) => {
    if (!llmConfig) {
      toast.error('Configure seu modelo de IA primeiro');
      setShowLLMConfig(true);
      return;
    }

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post(