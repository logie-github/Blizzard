package rig;
import java.util.*;
import com.etheller.warsmash.util.CampaignProgress;
/** Checks CampaignProgress: which campaigns and missions show as missions are won (no host: in memory). */
public class ProgressCheck { public static void main(String[] a) {
  CampaignProgress.setCampaigns(List.of(List.of("Maps\\Campaign\\Prologue01.w3m", "Maps\\Campaign\\Prologue02.w3m"), List.of("Maps\\Campaign\\Human01.w3m", "Maps\\Campaign\\Human02.w3m", "Maps\\Campaign\\Human02Interlude.w3m")));
  CampaignProgress.setProfile("A");
  Runnable show = () -> System.out.println("campaigns " + CampaignProgress.isCampaignAvailable(0) + "," + CampaignProgress.isCampaignAvailable(1) + " prologue " + CampaignProgress.isMissionAvailable(0, 0) + "," + CampaignProgress.isMissionAvailable(0, 1) + " human " + CampaignProgress.isMissionAvailable(1, 0) + "," + CampaignProgress.isMissionAvailable(1, 1) + "," + CampaignProgress.isMissionAvailable(1, 2));
  show.run();
  CampaignProgress.openMission(0, 1); System.out.print("Prologue01 won: "); show.run();
  CampaignProgress.openCampaign(1); System.out.print("Prologue02 won: "); show.run();
  CampaignProgress.openMissionByFile("maps/campaign/human02.w3m"); System.out.print("Human01 won (ChangeLevel): "); show.run();
  CampaignProgress.setProfile("B"); System.out.print("profile B: "); show.run();
} }
