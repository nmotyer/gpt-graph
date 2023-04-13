<script lang="ts">
    export let data: { [key: string]: any }[];
    import { onMount } from 'svelte';
    import { slide } from 'svelte/transition';

    let init = false;
    onMount(() => {
    init = true;
  });
  </script>
  
  <table class="min-w-full divide-y divide-gray-200 mt-auto">
    <thead class="bg-gray-50">
      <tr>
        {#each Object.keys(data[0]) as key}
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            {key}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
      {#each data as row}
        {#if init}
          <tr transition:slide|local={{axis: 'y', duration: 400}}>
          {#each Object.values(row) as value}
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {value}
            </td>
          {/each}
        </tr>
        {/if}
      {/each}
    </tbody>
  </table>
  
  <style>
    table {
      border-collapse: collapse;
    }
  
    th,
    td {
      border: 1px solid gray;
    }
  
    th {
      background-color: #f2f2f2;
      font-weight: bold;
    }
  
    td {
      padding: 0.5rem;
    }
  </style>
  