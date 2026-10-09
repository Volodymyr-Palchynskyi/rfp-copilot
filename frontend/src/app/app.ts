import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ProposalPage } from './proposal/proposal-page';

@Component({
  imports: [RouterOutlet, ProposalPage],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {}
