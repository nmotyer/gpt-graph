<script lang="ts">
	import { fade, fly } from 'svelte/transition';

	// import components
	import DataTable from '../components/data-table.svelte';
  import ChatWindow from '../components/chat-window.svelte';
  import ToolBar from '../components/toolbar.svelte';

	// declare variables used on page
	let tableData: { [key: string]: any; }[];
	let raw_results: { [key: string]: any; }[];
	let scriptContent: string;
  let newScript: HTMLScriptElement;
  let promptLabel: string;

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			event.preventDefault();
		}
    if (event.key === 'Enter' && (event.target as HTMLTextAreaElement)?.value.trim() !== '') {
      // Call your function here
      promptLabel = (event.target as HTMLTextAreaElement)?.value.trim()
      console.log('Enter key pressed and text exists in the textarea');
	  const text: string = (event.target as HTMLTextAreaElement)?.value.trim();
      postText(text)
    }
  }

  async function postText(text: string) {
    const endpoint = 'http://localhost:5000/data';
    const promptData = { 'prompt': text };
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(promptData)
      });
      if (response.ok) {
        const responseData = await response.json();
        console.log(responseData);
		tableData = responseData;
		raw_results = tableData;
		var resultScript = document.createElement("script");
		var inlineResult = document.createTextNode(`var raw_results = ${JSON.stringify(tableData.copyWithin(0, 0))}`);
		resultScript.appendChild(inlineResult);
		// (document as any).raw_results = tableData.copyWithin(-1, 0);
		document.head.appendChild(resultScript);
		fetchScript(raw_results);
      } else {
        console.error(`HTTP error: ${response.status}`);
      }
    } catch (error) {
      console.error(`Network error: ${error}`);
    }
  }

  async function fetchScript(dataToGraph: any) {
	console.log("fetching graph script")
    const endpoint = 'http://localhost:5000/graph';
    const dataForGPT = { 'data': dataToGraph };
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataForGPT)
      });
      if (response.ok) {
		const responseGraphData = await response.json();
		scriptContent = responseGraphData.script;
		console.log(scriptContent)
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
		var inlineScript = document.createTextNode(scriptContent);
		newScript.appendChild(inlineScript); 
		document.head.appendChild(newScript);

      } else {
        console.error(`HTTP error: ${response.status}`);
      }
    } catch (error) {
      console.error(`Network error: ${error}`);
    }
  }

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
  <div class="w-full">
    
  </div>
    <div class="w-full mt-auto">
      {#if tableData}
      <div transition:fly={{duration:200}} class="p-6 -mb-6">
        <DataTable data={tableData} />
      </div>
    {/if}
      {#if promptLabel}
        <p transition:fly={{y: 200, duration:200}} class="font-bold text-lg h-full p-2">{promptLabel}</p>
      {/if}
      <div class=" sticky">
        <ChatWindow />
      </div>
      
      <textarea class="w-full p-2 font-bold text-lg resize-none shadow-inner drop-shadow" on:keydown={handleKeyPress}></textarea>
    </div>
</section>

  <style>
	section {
	  flex: 1;
	}
  </style>
  
