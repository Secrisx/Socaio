import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';

export default function Chat() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to main page since chat functionality is integrated
    router.push('/');
  }, [router]);

  return (
    <Head>
      <title>Redirecting... - Socaio</title>
    </Head>
  );
}