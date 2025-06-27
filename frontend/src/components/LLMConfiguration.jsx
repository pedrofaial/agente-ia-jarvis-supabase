import React, { useState, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { 
  Cog6ToothIcon, 
  KeyIcon, 
  CpuChipIcon,
  InformationCircleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const LLM_MODELS = [
  { value: 'openai/gpt-4-turbo-preview', label: 'GPT-4 Turbo', provider: 'OpenAI', cost: '$$$' },
  { value: 'openai/gpt-4', label: 'GPT-4', provider: 'OpenAI', cost: '$$$' },
  { value: 'openai/gpt-3.5-turbo', label: 'GPT-3.5 Turbo', provider: 'OpenAI', cost: '$' },
  { value: 'anthropic/claude-3-opus', label: 'Claude 3 Opus', provider: 'Anthropic', cost: '$$$' },
  { value: 'anthropic/claude-3-sonnet', label: 'Claude 3 Sonnet', provider: 'Anthropic', cost: '$$' },
  { value: 'anthropic/claude-3-haiku', label: 'Claude 3 Haiku', provider: 'Anthropic', cost: '$' },
  { value: 'google/gemini-pro', label: 'Gemini Pro', provider: 'Google', cost: '$$' },
  { value: 'google/gemini-1.5-pro', label: 'Gemini 1.5 Pro', provider: 'Google', cost: '$$$' },
  { value: 'mistralai/mixtral-8x7b', label: 'Mixtral 8x7B', provider: 'Mistral', cost: '$$' },
  { value: 'meta-llama/llama-3-70b', label: 'Llama 3 70B', provider: 'Meta', cost: '$$' }
];

export default function LLMConfiguration({ isOpen, onClose, onSave }) {
  const [config, setConfig] = useState({
    openrouter_api_key: '',
    preferred_model: 'openai/gpt-3.5-turbo',
    temperature: 0.7
  });
  const [showApiKey, setShowApiKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Load saved config from localStorage
  useEffect(() => {
    const savedConfig = localStorage.getItem('llm_config');
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig));
    }
  }, []);

  const handleSave = async () => {
    if (!config.openrouter_api_key) {
      toast.error('Por favor, insira sua chave API do OpenRouter');
      return;
    }

    setIsSaving(true);
    try {
      // Save to localStorage
      localStorage.setItem('llm_config', JSON.stringify(config));
      
      // Call parent save handler
      await onSave(config);
      
      toast.success('Configurações salvas com sucesso!');
      onClose();
    } catch (error) {
      toast.error('Erro ao salvar configurações');
    } finally {
      setIsSaving(false);
    }
  };