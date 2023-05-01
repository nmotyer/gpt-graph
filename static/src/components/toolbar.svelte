<script lang="ts">
    import { io } from 'socket.io-client';

    let isVisible = false;
    let messages: object[];
    let tableData: object[];
    let summary: string;
    let title: string;
    let selectTool: string; // Current selected tool

    const socket = io('http://localhost:5000');
  
    function showToolbar() {
      isVisible = true;
    }
  
    function hideToolbar() {
      isVisible = false;
    }

      // subscribe to stores
  import { messagesStore, tableStore, summaryStore, titleStore } from '../store';
  $: {
    messages = $messagesStore;
  }
  $: {
    tableData = $tableStore;
  }
  $: {
    summary = $summaryStore;
  }
  $: {
    title = $titleStore;
  }

  function addMessage(message: object) {
    // Update the messagesStore by appending a new message
    messagesStore.update(currentMessages => [
      ...currentMessages,
      message
    ]);
  }

  function fetchSummary() {
    if (tableData.length > 0) {
      const data = tableData.slice(0,10)
      console.log('fetching summary');
      socket.emit('summarise', { 'data': data, 'title':  title});

      // messages = [...messages, { id: Date.now(), content: data, client: true }];
      addMessage({ id: Date.now(), content: Array.isArray(data)? JSON.stringify(data.slice(0,3)) + ' ...': 'invalid data', client: true })
    }
  }

  socket.on('response', (data: any) => {
    // Handle the response data
    // Place code to handle different events here based on the data received
    if (data.type == 'message') {
      addMessage({ id: Date.now(), content: data.message })
      summaryStore.set(data.message)
    }
  })

    async function getIdea() {
    const requestBody: object = { title: 'New Idea', description: 'Idea Description' };
    const response = await fetch('http://localhost:5000/idea', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    const data = await response.json();
    console.log(data)
  }
  </script>
  
  <!-- svelte-ignore a11y-mouse-events-have-key-events -->
  <div id="invisible-section" class="toolbar fixed right-0 top-0 h-screen w-12 opacity-5 z-50" on:mouseover={showToolbar} on:mouseleave={hideToolbar}></div>
   <!-- svelte-ignore a11y-mouse-events-have-key-events -->
  <div class="toolbar fixed right-0 top-0 h-screen w-20 bg-gray-500 z-50" on:mouseover={showToolbar} on:mouseleave={hideToolbar} style="{ isVisible ? 'transform: translateX(0);' : 'transform: translateX(12rem);' }">
    
    <ul class="flex flex-col items-center justify-center h-full">
      <li class="my-4">
        <!-- svelte-ignore a11y-invalid-attribute -->
        <a href="#" class="text-white hover:text-gray-200" on:click={() => (selectTool = 'select')}><i class="fas fa-mouse-pointer"></i></a>
      </li>
      <li class="my-4">
        <a href="#" class="text-white hover:text-yellow-400" on:click={getIdea}><i class="fas fa-lightbulb"></i></a>
      </li>
      <li class="my-4">
        <a href="#" class="text-white hover:text-gray-200" on:click={fetchSummary}><i class="fas fa-list"></i></a>
      </li>
      <li class="my-4">
        <a href="#" class="text-white hover:text-blue-400"><i class="fas fa-save"></i></a>
      </li>
    </ul>
  </div>
  
  <style>
    .toolbar {
      transition: transform 0.2s ease-out;
    }
  
    .toolbar i {
      font-size: 1.5rem;
    }
  </style>
  