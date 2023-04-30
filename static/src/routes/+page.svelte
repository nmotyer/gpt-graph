<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { io } from 'socket.io-client';

  // import components
  import DataTable from '../components/data-table.svelte';
  import ChatWindow from '../components/chat-window.svelte';
  import ToolBar from '../components/toolbar.svelte';

  // declare variables used on page
  let tableData: object[];
  let raw_results: { [key: string]: any; }[];
  let scriptContent: string;
  let newScript: HTMLScriptElement;
  let promptLabel: string;
  let summary: string;

  let currentQueryTopic: string = 'data'

  // subscribe to stores
  import { messagesStore, tableStore, summaryStore, titleStore } from '../store';
  $: {
    messages = $messagesStore;
  }
  $: {
    tableData = $tableStore;
  }
  // Subscribe to the summaryStore to get updates
  const unsubscribe = summaryStore.subscribe(value => {
    summary = value;
  });

  function addMessage(message: object) {
    // Update the messagesStore by appending a new message
    messagesStore.update(currentMessages => [
      ...currentMessages,
      message
    ]);
  }

  const socket = io('http://localhost:5000');

  socket.on('response', (data: any) => {
    // Handle the response data
    // Place code to handle different events here based on the data received
    if (data.type == 'message' || data.type == 'error') {
      //messages = [...messages, { id: Date.now(), content: data.message }];
      addMessage({ id: Date.now(), content: data.message })
    }
    if (data.type == 'result' && data.topic == 'data') {
      console.log(data.result)
      var resultScript = document.createElement("script");
      var inlineResult = document.createTextNode(`var raw_results = ${JSON.stringify(data.result.copyWithin(0, 0))}`);
      resultScript.appendChild(inlineResult);
      // tableData = data.result.copyWithin(0, 0)
      if (Array.isArray(data.result)) {
      tableStore.update(currentState => [...data.result]);
    }
      document.head.appendChild(resultScript)
      fetchScript(data.result);
    }
    if (data.type == 'result' && data.topic == 'graph') {
      console.log(data)
      if (newScript) {
      document.getElementById('chartScript')?.remove()
      // destroy the old canvas
      document.getElementById('myChart')?.remove()
      // create a new one
      var newCanvas: HTMLElement = document.createElement('canvas')
      newCanvas.setAttribute("id", "myChart")
      document.getElementById('section')?.insertBefore(newCanvas, (document.getElementById('section') as HTMLElement)?.firstChild)
      }
      newScript = document.createElement("script");
      newScript.setAttribute('id', 'chartScript')
      var inlineScript = document.createTextNode(data.result);
      newScript.appendChild(inlineScript);
      console.log(data.result)
      // messages = [...messages, { id: Date.now(), content: data.result }];
      addMessage({ id: Date.now(), content: data.result })
      document.head.appendChild(newScript);
    }
    if (data.type == 'result' && data.topic == 'title') {
      promptLabel = data.result;
      titleStore.set(promptLabel)
      addMessage({ id: Date.now(), content: data.result })
    }

  });

// Initialize an empty array for messages
let messages: Array<object> = [];

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
    }
    if (event.key === 'Enter' && (event.target as HTMLTextAreaElement)?.value.trim() !== '') {
      promptLabel = '';
      promptLabel = (event.target as HTMLTextAreaElement)?.value.trim();
      console.log('Enter key pressed and text exists in the textarea');
      const text: string = (event.target as HTMLTextAreaElement)?.value.trim();
      // messages = [...messages, { id: Date.now(), content: text, client: true }];
      addMessage({ id: Date.now(), content: text, client: true })
      socket.emit('data', { 'prompt': text });
      socket.emit('suggest_title', {'data': text})
    }
  }

  function fetchScript(dataToGraph: any) {
    console.log('fetching graph script');
    socket.emit('graph', { 'data': dataToGraph });
  }

  // You can add a similar function for 'idea' WebSocket events if needed

</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>
<ToolBar />
<section class="flex flex-col justify-center items-center h-full" id="section">
	<!-- content here -->

	<canvas id="myChart" class="myChart -mb-6">
	</canvas>
  {#if summary.length > 0}
  <div class="p-4 bg-gray-100">
    <p id="typing-text" class="text-lg text-gray-800">
      {summary}
    </p>
  </div>
  {/if}
  
    <div class="w-full mt-auto">
      {#if tableData.length > 0}
      <div transition:fly={{duration:200}} class="p-6 -mb-6">
        <DataTable data={tableData} />
      </div>
    {/if}
      {#if promptLabel}
        <p transition:fly={{y: 200, duration:200}} class="font-bold text-lg h-full p-2">{promptLabel}</p>
      {/if}
      <div class="">
        <ChatWindow messages={messages} />
      </div>
      
      <textarea class="w-full p-2 font-bold text-lg resize-none shadow-inner drop-shadow" on:keydown={handleKeyPress}></textarea>
    </div>
</section>

  <style>
	section {
	  flex: 1;
	}

  @keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

#typing-text {
  animation: typing 2s steps(40) 0s forwards;
  white-space: pre-wrap;
  overflow: hidden;
  border-right: none;
}
  </style>
  
