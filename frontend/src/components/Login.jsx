import React, { useState } from 'react';
import { useSupabase } from '../contexts/SupabaseContext';
import { useNavigate } from 'react-router-dom';
import { 
  BuildingOfficeIcon,
  EnvelopeIcon,
  LockClosedIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export default function Login() {
  const { signIn } = useSupabase();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isSignUp) {
        // For sign up, would need to implement in context
        toast.error('Cadastro em desenvolvimento. Use login com credenciais existentes.');
      } else {
        const { error } = await signIn(formData.email, formData.password);
        if (!error) {
          navigate('/chat');
        }